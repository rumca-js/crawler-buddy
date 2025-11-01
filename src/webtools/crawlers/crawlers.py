"""
Provides cralwers implmenetation that can be used directly in program.

Some crawlers / scrapers cannot be easily called from a thread, etc, because of asyncio.
"""

import time
import threading
import urllib.parse

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

    def make_requests_call(self, request, stream):
        """
        This method can be overridden in subclasses to change the request behavior.
        """
        import requests

        return requests.get(
            request.url,
            headers=request.request_headers,
            timeout=request.timeout_s,
            verify=request.ssl_verify,
            cookies=request.cookies,
            stream=stream,
        )

    def build_requests(self):
        """
        Perform an HTTP GET request with total timeout control using threading.

        Notes:
        - stream=True defers the content download until accessed.
        - Overcomes the limitation of requests.get's timeout (which doesn't cover total duration).
        """

        def request_with_timeout(request, stream, result):
            try:
                result["response"] = self.make_requests_call(
                    request, stream
                )
            except Exception as e:
                result["exception"] = e

        def make_request_with_threading(request, stream):
            result = {"response": None, "exception": None}

            thread = threading.Thread(
                target=request_with_timeout,
                args=(request, stream, result),
            )
            thread.start()
            thread.join(request.timeout_s)

            if thread.is_alive():
                raise WebToolsTimeoutException("Request timed out")
            if result["exception"]:
                raise result["exception"]
            return result["response"]

        self.request.headers = self.get_request_headers()
        self.request.timeout_s = self.get_timeout_s()

        response = make_request_with_threading(
            request=self.request,
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
                cookies=self.request.cookies,
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

        try:
            answer = httpx.get(
                self.request.url,
                timeout=self.get_timeout_s(),
                verify=self.request.ssl_verify,
                headers=self.get_request_headers(),
                cookies=self.request.cookies,
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

        content = None
        text = None

        if answer:
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
