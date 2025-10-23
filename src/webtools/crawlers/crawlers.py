"""
Provides cralwers implmenetation that can be used directly in program.

Some crawlers / scrapers cannot be easily called from a thread, etc, because of asyncio.
"""

import json
import traceback
import time
from pathlib import Path
import shutil
import os
import subprocess
import threading
import urllib.parse
import tempfile

from utils.basictypes import fix_path_for_os

from webtoolkit import (
    RssPage,
    HtmlPage,
    PageResponseObject,
    CrawlerInterface,
    WebToolsTimeoutException,
    WebLogger,
    file_to_response,
    HTTP_STATUS_UNKNOWN,
    HTTP_STATUS_OK,
    HTTP_STATUS_USER_AGENT,
    HTTP_STATUS_TOO_MANY_REQUESTS,
    HTTP_STATUS_CODE_EXCEPTION,
    HTTP_STATUS_CODE_CONNECTION_ERROR,
    HTTP_STATUS_CODE_TIMEOUT,
    HTTP_STATUS_CODE_FILE_TOO_BIG,
    HTTP_STATUS_CODE_PAGE_UNSUPPORTED,
    HTTP_STATUS_CODE_SERVER_ERROR,
)


class RequestsCrawler(CrawlerInterface):
    """
    Python requests are based.

    Quirks:
     - timeout in requests defines timeout for stalled communication.
       this means you can be stuck if you read 1byte/second.
       This means we have to start a thread, and make timeout ourselves
    """

    def run(self):
        if not self.is_valid():
            return

        import requests

        WebLogger.debug("Requests Driver:{}".format(self.request.url))

        """
        stream argument allows us to read header before we fetch the page.
        SSL verification makes everything to work slower.
        """

        self.response = PageResponseObject(
            self.request.url,
            text=None,
            status_code=HTTP_STATUS_CODE_SERVER_ERROR,
            request_url=self.request.url,
        )

        try:
            request_result = self.build_requests()

            if request_result is None:
                self.response.add_error("Could not build response")
                return self.response

            self.response = PageResponseObject(
                url=request_result.url,
                text=None,
                status_code=request_result.status_code,
                headers=dict(request_result.headers),
                request_url=self.request.url,
            )
            if not self.is_response_valid():
                request_result.close()

                return self.response

            if self.request.request_type == "ping":
                request_result.close()
                return self.response

            # TODO do we want to check also content-type?

            content_type = self.response.get_content_type()

            if content_type and not self.response.is_content_type_text():
                self.response.binary = request_result.content
                request_result.close()
                return self.response
            else:
                encoding = self.get_encoding(self.response, request_result)
                if encoding:
                    request_result.encoding = encoding

                self.response = PageResponseObject(
                    url=request_result.url,
                    text=request_result.text,
                    status_code=request_result.status_code,
                    encoding=request_result.encoding,
                    headers=dict(request_result.headers),
                    binary=request_result.content,
                    request_url=self.request.url,
                )

                request_result.close()

        except requests.Timeout:
            WebLogger.debug("Url:{} timeout".format(self.request.url))
            self.response = PageResponseObject(
                self.request.url,
                text=None,
                status_code=HTTP_STATUS_CODE_TIMEOUT,
                request_url=self.request.url,
            )
            self.response.add_error("Url:{} Page timeout".format(self.request.url))

        except WebToolsTimeoutException:
            WebLogger.debug("Url:{} timeout".format(self.request.url))
            self.response = PageResponseObject(
                self.request.url,
                text=None,
                status_code=HTTP_STATUS_CODE_TIMEOUT,
                request_url=self.request.url,
            )
            self.response.add_error("Url:{} Page timeout".format(self.request.url))

        except requests.exceptions.ConnectionError:
            WebLogger.debug("Url:{} connection error".format(self.request.url))
            self.response = PageResponseObject(
                self.request.url,
                text=None,
                status_code=HTTP_STATUS_CODE_CONNECTION_ERROR,
                request_url=self.request.url,
            )
            self.response.add_error("Url:{} Connection error".format(self.request.url))

        except Exception as E:
            WebLogger.exc(E, "Url:{} General exception".format(self.request.url))

            self.response = PageResponseObject(
                self.request.url,
                text=None,
                status_code=HTTP_STATUS_CODE_EXCEPTION,
                request_url=self.request.url,
            )
            self.response.add_error("General page exception: {}".format(str(E)))

        return self.response

    def get_encoding(self, response, request_result):
        """
        The default assumed content encoding for text/html is ISO-8859-1 aka Latin-1 :( See RFC-2854. UTF-8 was too young to become the default, it was born in 1993, about the same time as HTML and HTTP.
        Use .content to access the byte stream, or .text to access the decoded Unicode stream.

        chardet does not work on youtube RSS feeds.
        apparent encoding does not work on youtube RSS feeds.
        """

        url = self.request.url

        encoding = response.get_encoding()
        if encoding:
            return encoding

        else:
            text = request_result.text
            # There might be several encoding texts, if so we do not know which one to use
            if response.is_content_html():
                p = HtmlPage(url, text)
                if p.is_valid():
                    if p.get_charset():
                        return p.get_charset()
            if response.is_content_rss():
                p = RssPage(url, text)
                if p.is_valid():
                    if p.get_charset():
                        return p.get_charset()

            # TODO this might trigger download of a big file
            text = text.lower()

            if text.count("encoding") == 1 and text.find('encoding="utf-8"') >= 0:
                return "utf-8"
            elif text.count("charset") == 1 and text.find('charset="utf-8"') >= 0:
                return "utf-8"

    def make_requests_call(self, url, headers, timeout, verify, stream):
        """
        This method can be overridden in subclasses to change the request behavior.
        """
        import requests

        return requests.get(
            url,
            headers=headers,
            timeout=timeout,
            verify=verify,
            stream=stream,
        )

    def build_requests(self):
        """
        Perform an HTTP GET request with total timeout control using threading.

        Notes:
        - stream=True defers the content download until accessed.
        - Overcomes the limitation of requests.get's timeout (which doesn't cover total duration).
        """

        def request_with_timeout(url, headers, timeout, verify, stream, result):
            try:
                result["response"] = self.make_requests_call(
                    url, headers, timeout, verify, stream
                )
            except Exception as e:
                result["exception"] = e

        def make_request_with_threading(url, headers, timeout_s, ssl_verify, stream):
            result = {"response": None, "exception": None}

            thread = threading.Thread(
                target=request_with_timeout,
                args=(url, headers, timeout_s, ssl_verify, stream, result),
            )
            thread.start()
            thread.join(timeout_s)

            if thread.is_alive():
                raise WebToolsTimeoutException("Request timed out")
            if result["exception"]:
                raise result["exception"]
            return result["response"]

        headers = self.get_request_headers()

        response = make_request_with_threading(
            url=self.request.url,
            headers=headers,
            timeout_s=self.get_timeout_s(),
            ssl_verify=self.request.ssl_verify,
            stream=True,
        )
        return response

    def is_valid(self):
        try:
            import requests

            return True
        except Exception as E:
            print(str(E))
            return False

    def ping(self):
        import requests

        user_agent = self.get_user_agent()
        headers = self.get_default_headers()
        headers["User-Agent"] = user_agent
        url = self.request.url

        response = None
        try:
            with requests.get(
                url=url,
                headers=headers,
                timeout=20,
                verify=False,
                stream=True,
            ) as response:
                response = PageResponseObject(
                    url,
                    text=None,
                    status_code=response.status_code,
                    request_url=url,
                )

        except requests.Timeout:
            WebLogger.debug("Url:{} timeout".format(url))
            response = PageResponseObject(
                url,
                text=None,
                status_code=HTTP_STATUS_CODE_TIMEOUT,
                request_url=url,
            )

        except requests.exceptions.ConnectionError:
            WebLogger.debug("Url:{} connection error".format(url))
            response = PageResponseObject(
                url,
                text=None,
                status_code=HTTP_STATUS_CODE_CONNECTION_ERROR,
                request_url=url,
            )

        except Exception as E:
            WebLogger.exc(E, "Url:{} General exception".format(url))

            response = PageResponseObject(
                url,
                text=None,
                status_code=HTTP_STATUS_CODE_EXCEPTION,
                request_url=url,
            )

        return response


class CurlCffiCrawler(CrawlerInterface):
    """
    Python steath requests
    """

    def run(self):
        if not self.is_valid():
            return

        self.response = PageResponseObject(
            self.request.url,
            text=None,
            status_code=HTTP_STATUS_CODE_SERVER_ERROR,
            request_url=self.request.url,
        )

        answer = self.build_requests()

        if answer:
            self.response = PageResponseObject(
                self.request.url,
                status_code=answer.status_code,
                request_url=self.request.url,
                headers=answer.headers,
            )
            if not self.is_response_valid():
                return self.response

        content = getattr(answer, "content", None)
        text = getattr(answer, "text", None)

        if answer and content:
            self.response = PageResponseObject(
                self.request.url,
                binary=content,
                status_code=answer.status_code,
                request_url=self.request.url,
                headers=answer.headers,
            )

            return self.response

        elif text:
            self.response = PageResponseObject(
                self.request.url,
                binary=None,
                text=text,
                status_code=answer.status_code,
                request_url=self.request.url,
                headers=answer.headers,
            )

        elif answer:
            self.response = PageResponseObject(
                self.request.url,
                binary=None,
                text=None,
                status_code=answer.status_code,
                request_url=self.request.url,
                headers=answer.headers,
            )

        if self.response:
            return self.response

    def build_requests(self):
        import curl_cffi
        from curl_cffi import requests
        from curl_cffi.requests.exceptions import ConnectionError

        headers = self.get_request_headers()

        try:
            answer = curl_cffi.get(
                self.request.url,
                timeout=self.get_timeout_s(),
                verify=self.request.ssl_verify,
                impersonate="chrome",
                #headers=headers,
                # stream=True, # TODO
            )
            return answer
        except ConnectionError as E:
            self.response = PageResponseObject(
                self.request.url,
                text=None,
                status_code=HTTP_STATUS_CODE_CONNECTION_ERROR,
                request_url=self.request.url,
            )
            self.response.add_error("Url:{} Cannot create request".format(str(E)))
        except Exception as E:
            self.response = PageResponseObject(
                self.request.url,
                text=None,
                status_code=HTTP_STATUS_CODE_EXCEPTION,
                request_url=self.request.url,
            )
            self.response.add_error("Url:{} Cannot create request".format(str(E)))

    def is_valid(self):
        try:
            from curl_cffi import requests

            return True
        except Exception as E:
            print(str(E))
            return False


class HttpxCrawler(CrawlerInterface):
    """
    Python httpx
    """

    def run(self):
        if not self.is_valid():
            return

        self.response = PageResponseObject(
            self.request.url,
            text=None,
            status_code=HTTP_STATUS_CODE_SERVER_ERROR,
            request_url=self.request.url,
        )

        answer = self.build_requests()

        if answer:
            self.response = PageResponseObject(
                self.request.url,
                status_code=answer.status_code,
                request_url=self.request.url,
                headers=answer.headers,
            )
            if not self.is_response_valid():
                return self.response

        content = getattr(answer, "content", None)
        text = getattr(answer, "text", None)

        if answer and content:
            self.response = PageResponseObject(
                self.request.url,
                binary=content,
                status_code=answer.status_code,
                request_url=self.request.url,
                headers=answer.headers,
            )

            return self.response

        elif text:
            self.response = PageResponseObject(
                self.request.url,
                binary=None,
                text=text,
                status_code=answer.status_code,
                request_url=self.request.url,
                headers=answer.headers,
            )

        elif answer:
            self.response = PageResponseObject(
                self.request.url,
                binary=None,
                text=None,
                status_code=answer.status_code,
                request_url=self.request.url,
                headers=answer.headers,
            )

        if self.response:
            return self.response

    def build_requests(self):
        import httpx

        headers = self.get_request_headers()

        try:
            answer = httpx.get(
                self.request.url,
                timeout=self.get_timeout_s(),
                verify=self.request.ssl_verify,
                headers=headers,
                follow_redirects=True,
                # stream=True, # TODO
            )
            return answer
        except Exception as E:
            self.response = PageResponseObject(
                self.request.url,
                text=None,
                status_code=HTTP_STATUS_CODE_CONNECTION_ERROR,
                request_url=self.request.url,
            )
            self.response.add_error("Url:{} Cannot create request".format(str(E)))

    def is_valid(self):
        try:
            import httpx

            return True
        except Exception as E:
            print(str(E))
            return False


class StealthRequestsCrawler(CrawlerInterface):
    """
    Python steath requests
    """

    def run(self):
        if not self.is_valid():
            return

        self.response = PageResponseObject(
            self.request.url,
            text=None,
            status_code=HTTP_STATUS_CODE_SERVER_ERROR,
            request_url=self.request.url,
        )

        answer = self.build_requests()

        content = answer.content
        text = answer.text

        if answer and content:
            self.response = PageResponseObject(
                self.request.url,
                binary=content,
                status_code=answer.status_code,
                request_url=self.request.url,
                headers=answer.headers,
            )

            if not self.is_response_valid():
                return self.response

        elif answer and text:
            self.response = PageResponseObject(
                self.request.url,
                binary=None,
                text=text,
                status_code=answer.status_code,
                request_url=self.request.url,
                headers=answer.headers,
            )

        elif answer:
            self.response = PageResponseObject(
                self.request.url,
                binary=None,
                text=None,
                status_code=answer.status_code,
                request_url=self.request.url,
                headers=answer.headers,
            )

            return self.response

        if self.response:
            return self.response

    def build_requests(self):
        import stealth_requests as requests

        try:
            answer = requests.get(
                self.request.url,
                timeout=self.get_timeout_s(),
                verify=self.request.ssl_verify,
                # stream=True,   # TODO does not work with it
            )
            return answer
        except Exception as E:
            self.response = PageResponseObject(
                self.request.url,
                text=None,
                status_code=HTTP_STATUS_CODE_CONNECTION_ERROR,
                request_url=self.request.url,
            )
            self.response.add_error("Url:{} Connection error".format(self.request.url))

    def is_valid(self):
        try:
            import stealth_requests as requests

            return True
        except Exception as E:
            print(str(E))
            return False


class ScriptCrawler(CrawlerInterface):
    """
    Used to run script to obtain URL response.
    Calls script, and receives reply in the file.

    Note:
     If we have multiple instances/workspaces each can write their own output file
    """

    def __init__(
        self,
        request=None,
        url=None,
        cwd=None,
        script=None,
        settings=None,
    ):
        self.cwd = cwd
        self.script = script

        super().__init__(
            request=request,
            url=url,
            settings=settings,
        )

    def get_response_file(self):
        response_file = super().get_response_file()

        if not response_file:
            from ..webconfig import WebConfig

            if WebConfig.script_responses_directory is not None:
                response_dir = Path(WebConfig.script_responses_directory)
            else:
                response_dir = Path("storage")

            response_file = self.get_main_path() / response_dir / self.get_response_file_name()
            return response_file

    def get_main_path(self):
        file_path = os.path.realpath(__file__)
        full_path = Path(file_path)
        return full_path.parents[3]

    def set_settings(self, settings):
        super().set_settings(settings)

        inner = self.settings["settings"]

        if inner and "script" in inner and inner["script"]:
            self.script = inner["script"]

        if inner and "cwd" in inner:
            self.cwd = inner["cwd"]

        if not self.cwd:
            self.cwd = self.get_main_path()

        if inner and "remote_server" in inner:
            return

    def run(self):
        if not self.is_valid():
            return

        inner = self.settings["settings"]

        if inner and "remote_server" in inner:
            return self.run_via_server(inner["remote_server"])
        else:
            return self.run_via_file()

    def run_via_server(self, remote_server):
        self.response = PageResponseObject(
            self.request.url,
            text=None,
            status_code=HTTP_STATUS_CODE_SERVER_ERROR,
            request_url=self.request.url,
        )

        script = self.script + ' --url "{}" --remote-server="{}" --timeout={}'.format(
            self.request.url, remote_server, self.get_timeout_s()
        )

        # WebLogger.error("Response:{}".format(self.response_file))
        # WebLogger.error("CWD:{}".format(self.cwd))
        # WebLogger.error("maintl:{}".format(self.get_main_path()))
        # WebLogger.error("script:{}".format(script))

        print("Running CWD:{} script:{}".format(self.cwd, script))

        try:
            p = subprocess.run(
                script,
                shell=True,
                capture_output=True,
                cwd=self.cwd,
                timeout=self.get_timeout_s() + 5,  # add more time for closing browser, etc
            )
        except subprocess.TimeoutExpired as E:
            WebLogger.debug(E, "Timeout on running script")

            self.response = PageResponseObject(
                self.request.url,
                text=None,
                status_code=HTTP_STATUS_CODE_TIMEOUT,
                request_url=self.request.url,
            )
            return self.response
        except ValueError as E:
            WebLogger.exc(E, "Incorrect script call {}".format(script))
            return self.response

        if p.returncode != 0:
            if p.stdout:
                stdout_str = p.stdout.decode()
                if stdout_str != "":
                    WebLogger.error(stdout_str)

            if p.stderr:
                stderr_str = p.stderr.decode()
                if stderr_str and stderr_str != "":
                    WebLogger.error("Url:{}. {}".format(self.request.url, stderr_str))

            WebLogger.error(
                "Url:{}. Script:'{}'. Return code invalid:{}. Path:{}".format(
                    self.request.url,
                    script,
                    p.returncode,
                    self.cwd,
                )
            )

        import requests
        from ..remoteserver import RemoteServer

        url = f"{remote_server}/findj?url={self.request.url}"
        response = requests.get(url)

        if response.status_code == 200:
            try:
                data = response.json()

                server = RemoteServer("")
                self.response = server.get_response(data)

                return self.response

            except ValueError as E:
                print("Response content is not valid JSON. {}".format(E))
        else:
            WebLogger.error(
                f"Url:{self.request.url}: Failed to fetch data. Status code: {response.status_code}"
            )

            self.response = PageResponseObject(
                self.request.url,
                text=None,
                status_code=HTTP_STATUS_CODE_SERVER_ERROR,
                request_url=self.request.url,
            )

    def run_via_file(self):
        self.response = PageResponseObject(
            self.request.url,
            text=None,
            status_code=HTTP_STATUS_CODE_SERVER_ERROR,
            request_url=self.request.url,
        )

        response_file_location = Path(self.get_response_file())
        print("Running via file {}".format(response_file_location))

        if len(response_file_location.parents) > 1:
            response_dir = response_file_location.parents[1]
            if not response_dir.exists():
                response_dir.mkdir(parents=True, exist_ok=True)

        file_abs = response_file_location
        if file_abs.exists():
            file_abs.unlink()

        script = self.script + ' --url "{}" --output-file="{}" --timeout={}'.format(
            self.request.url, self.get_response_file(), self.get_timeout_s()
        )

        # WebLogger.error("Response:{}".format(self.response_file))
        # WebLogger.error("CWD:{}".format(self.cwd))
        # WebLogger.error("maintl:{}".format(self.get_main_path()))
        # WebLogger.error("script:{}".format(script))
        print("Running script:{}".format(script))

        try:
            p = subprocess.run(
                script,
                shell=True,
                capture_output=True,
                cwd=self.cwd,
                timeout=self.get_timeout_s() + 10,  # add more time for closing browser, etc
            )
        except subprocess.TimeoutExpired as E:
            WebLogger.debug(E, "Timeout on running script")

            self.response = PageResponseObject(
                self.request.url,
                text=None,
                status_code=HTTP_STATUS_CODE_TIMEOUT,
                request_url=self.request.url,
            )
            return self.response
        except ValueError as E:
            WebLogger.exc(E, "Incorrect script call {}".format(script))
            return self.response

        if p.returncode != 0:
            if p.stdout:
                stdout_str = p.stdout.decode()
                if stdout_str != "":
                    WebLogger.error(stdout_str)

            if p.stderr:
                stderr_str = p.stderr.decode()
                if stderr_str and stderr_str != "":
                    WebLogger.error("Url:{}. {}".format(self.request.url, stderr_str))

            WebLogger.error(
                "Url:{}. Script:'{}'. Return code invalid:{}. Path:{}".format(
                    self.request.url,
                    script,
                    p.returncode,
                    self.cwd,
                )
            )

        if file_abs.exists():
            self.response = file_to_response(str(file_abs))

            file_abs.unlink()

            return self.response

        else:
            WebLogger.error(
                "Url:{}. Response file does not exist:{}".format(
                    self.request.url, str(response_file_location)
                )
            )

            self.response = PageResponseObject(
                self.request.url,
                text=None,
                status_code=HTTP_STATUS_CODE_SERVER_ERROR,
                request_url=self.request.url,
            )

    def process_input(self):
        """
        TODO these three functions below, could be used
        """
        if not self.script:
            self.operating_path = None
            return

        self.operating_path = self.get_operating_dir()

    def get_response_file_name(self):
        file_name_url_part = fix_path_for_os(self.request.url)
        file_name_url_part = file_name_url_part.replace("\\", "")
        file_name_url_part = file_name_url_part.replace("/", "")
        file_name_url_part = file_name_url_part.replace("@", "")

        response_file = "response_{}.txt".format(file_name_url_part)
        return response_file

    def get_operating_dir(self):
        from ..webconfig import WebConfig

        file_path = os.path.realpath(__file__)
        full_path = Path(file_path)

        if WebConfig.script_operating_dir is None:
            operating_path = full_path.parents[2]
        else:
            operating_path = Path(WebConfig.script_operating_dir)

        if not operating_path.exists():
            WebLogger.error("Operating path does not exist: {}".format(operating_path))
            return

        return operating_path

    def close(self):
        response_file = self.get_response_file()
        if response_file:
            response_file_location = Path(response_file)
            if response_file_location.exists():
                response_file_location.unlink()

    def is_valid(self):
        if not self.script:
            return False

        return True


class ScriptCrawlerInterface(CrawlerInterface):
    """
    Interface that can be inherited by any browser, browser engine, crawler
    """

    def __init__(self, parser, request, file_name, scraper_name):
        settings = None
        self.parser = parser

        if parser.args.remote_server:
            settings = {"remote_server": parser.args.remote_server}
        elif not settings:
            settings = {}

        file_name = os.path.relpath(file_name, os.getcwd())

        settings["name"] = scraper_name
        settings["crawler"] = ScriptCrawler.__name__
        settings["settings"] = {}
        settings["settings"]["script"] = file_name
        settings["settings"]["response_file"] = parser.args.output_file

        super().__init__(
            request, settings=settings
        )


class BotasaurusCrawler(CrawlerInterface):
    """
    Web crawler using Botasaurus
    """

    def run(self):
        if not self.is_valid():
            return

        self.response = PageResponseObject(
            self.request.url,
            text=None,
            status_code=HTTP_STATUS_CODE_SERVER_ERROR,
            request_url=self.request.url,
        )

        try:
            result = self.build_browser_request()

            if not result:
                return self.response

            html = result.get("html")
            status_code = result.get("status_code", 200)
            headers = result.get("headers", {})

            self.response = PageResponseObject(
                self.request.url,
                text=html,
                status_code=status_code,
                request_url=self.request.url,
                headers=headers,
            )

            if not self.is_response_valid():
                return self.response

            return self.response

        except Exception as e:
            self.response = PageResponseObject(
                self.request.url,
                text=None,
                status_code=HTTP_STATUS_CODE_CONNECTION_ERROR,
                request_url=self.request.url,
            )
            self.response.add_error(
                f"Url: {str(e)} Cannot render or fetch with Botasaurus"
            )
            return self.response

    def build_browser_request(self):
        from botasaurus import bts

        """
        Launch Botasaurus and retrieve HTML content
        """

        @bts.default
        def get_html(driver):
            driver.get(self.request.url)
            html = driver.page_source
            return {
                "html": html,
                "status_code": 200,  # Botsaurus doesn't expose this, assume OK
                "headers": {},  # You could mock or skip headers if irrelevant
            }

        return get_html()

    def is_valid(self):
        try:
            from botasaurus import bts

            return True
        except Exception as E:
            print(str(E))
            return False
