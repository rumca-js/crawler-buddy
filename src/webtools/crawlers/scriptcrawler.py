"""
Provides cralwers implmenetation that can be used directly in program.

Some crawlers / scrapers cannot be easily called from a thread, etc, because of asyncio.
"""

import json
import traceback
import hashlib
import time
from pathlib import Path
import shutil
import os
import subprocess
import threading
import urllib.parse
import tempfile
import requests

from utils.basictypes import fix_path_for_os

from webtoolkit import (
    RssPage,
    HtmlPage,
    PageResponseObject,
    RemoteUrl,
    RemoteServer,
    CrawlerInterface,
    WebToolsTimeoutException,
    WebLogger,
    file_to_response,
    request_to_file,
    request_to_json,
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
        self.hash = None

        super().__init__(
            request=request,
            url=url,
        )

    def get_response_file(self):
        from ..webconfig import WebConfig

        if WebConfig.script_responses_directory is not None:
            response_dir = Path(WebConfig.script_responses_directory)
        else:
            response_dir = Path("storage")

        file_path = self.get_main_path() / response_dir / self.get_response_file_name()
        return file_path

    def get_request_file(self):
        response_dir = Path("storage")

        file_path = self.get_main_path() / response_dir / self.get_request_file_name()
        return file_path

    def makedirs(self):
        response_dir = Path("storage")
        path = self.get_main_path() / response_dir
        path.mkdir(parents=True, exist_ok=True)

        """
        if len(response_file_location.parents) > 1:
            response_dir = response_file_location.parents[0]
            WebLogger.debug(str(response_dir))
            if not response_dir.exists():
                response_dir.mkdir(parents=True, exist_ok=True)
        """

    def get_main_path(self):
        file_path = os.path.realpath(__file__)
        full_path = Path(file_path)
        return full_path.parents[3]

    def run_internal(self):
        if self.script is None:
            self.script = self.request.settings.get('script')
            if self.script is None:
                self.add_error("Script is None")
                return

        self.hash = self.get_request_hash()

        if not self.is_valid():
            return

        remote_server = self.request.settings.get("remote_server")

        if remote_server:
            return self.run_via_server(remote_server)
        else:
            return self.run_via_file()

    def run_via_server(self, remote_server):
        url = self.request.url
        crawl_id = self.request.settings.get("crawl_id")
        timeout_s = self.get_timeout_s()

        """
        TODO ?
        self.makedirs()
        request_file = self.get_request_file()
        if request_file.exists():
            request_file.unlink()
        request_to_file(self.request, request_file)
        """

        script = self.script + f' --url "{url}" --remote-server="{remote_server}" --timeout={timeout_s} --request-stdin'

        # TODO pass headers and cookies

        # WebLogger.error("Response:{}".format(self.response_file))
        # WebLogger.error("CWD:{}".format(self.cwd))
        # WebLogger.error("maintl:{}".format(self.get_main_path()))
        # WebLogger.error("script:{}".format(script))

        WebLogger.debug("Running CWD:{} via server with script:{}".format(self.cwd, script))

        request_json = request_to_json(self.request)

        try:
            p = subprocess.run(
                script,
                shell=True,
                input=json.dumps(request_json),
                text=True,
                capture_output=True,
                cwd=self.cwd,
                timeout=self.get_timeout_s() + 5,  # add more time for closing browser, etc
            )

        except subprocess.TimeoutExpired as E:
            WebLogger.debug(E, "Timeout on running script")

            try:
                p.kill()
            except Exception as E:
                WebLogger.exc(E, "Could not kill process")

            self.set_timeout_response()
            return self.response

        except ValueError as E:
            self.set_exception_response(E)
            WebLogger.exc(E, "Incorrect script call {}".format(script))
            return self.response

        if p.returncode != 0:
            if p.stdout:
                stdout_str = p.stdout
                if stdout_str != "":
                    WebLogger.error(stdout_str)

            if p.stderr:
                stderr_str = p.stderr
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
            self.add_error("Return code invalid: {}".format(p.returncode))

        url = self.request.url
        crawler_name = self.request.crawler_name
        handler_name = self.request.handler_name

        server = RemoteServer(remote_server)
        json_data = server.findj(url=url, crawler_name=crawler_name, handler_name=handler_name)

        if json_data:
            url = RemoteUrl(all_properties = json_data)
            self.response = url.get_response()

            return self.response
        else:
            WebLogger.error(
                f"Url:{self.request.url}: Failed to fetch data.")
            
            self.add_error("Failed to fetch data")

    def run_via_file(self):
        response_file_location = Path(self.get_response_file())
        WebLogger.debug("Running via file {}".format(response_file_location))

        self.makedirs()

        request_file = self.get_request_file()
        if request_file.exists():
            request_file.unlink()
        request_to_file(self.request, request_file)

        if not request_file.exists():
            WebLogger.error("File does not exist")
            time.sleep(1)

        if response_file_location.exists():
            response_file_location.unlink()

        url = self.request.url
        timeout_s = self.get_timeout_s()
        output_file = response_file_location

        script = self.script + f' --url "{url}" --output-file="{output_file}" --timeout={timeout_s} --request-file={request_file}'

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
            WebLogger.debug("Timeout on running script {E}")

            self.set_timeout_response()
            return self.response
        except ValueError as E:
            WebLogger.exc(E, "Incorrect script call {}".format(script))
            self.set_exception_response(E)

            return self.response

        if p.returncode != 0:
            WebLogger.error(
                "Url:{}. Script:'{}'. Return code invalid:{}. Path:{}".format(
                    self.request.url,
                    script,
                    p.returncode,
                    self.cwd,
                )
            )
            self.add_error("Return code invalid: {}".format(p.returncode))

            if p.stdout:
                stdout_str = p.stdout.decode()
                if stdout_str != "":
                    WebLogger.error(stdout_str)

            if p.stderr:
                stderr_str = p.stderr.decode()
                if stderr_str and stderr_str != "":
                    WebLogger.error("Url:{}. {}".format(self.request.url, stderr_str))

        if response_file_location.exists():
            self.response = file_to_response(str(response_file_location))

            response_file_location.unlink()

            return self.response

        else:
            WebLogger.error(
                "Url:{}. Response file does not exist:{}".format(
                    self.request.url, str(response_file_location)
                )
            )

        return self.response

    def process_input(self):
        """
        TODO these three functions below, could be used
        """
        if not self.script:
            self.operating_path = None
            return

        self.operating_path = self.get_operating_dir()

    def get_request_hash(self):
        crawl_id = str(self.request.settings.get("crawl_id"))
        crawler_name = str(self.request.crawler_name)
        handler_name = str(self.request.handler_name)
        text = self.request.url + crawl_id + crawler_name + handler_name

        string = hashlib.md5(text.encode("utf-8")).hexdigest()
        return string

    def get_response_file_name(self):
        response_file = f"response_{self.hash}.txt"
        return response_file

    def get_request_file_name(self):
        response_file = f"request_{self.hash}.txt"
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
            self.add_error("Operating path does not exist: {}".format(operating_path))
            return

        return operating_path

    def close(self):
        try:
            request_file = self.get_request_file()
            if request_file.exists():
                request_file.unlink()
            response_file = self.get_response_file()
            if response_file.exists():
                response_file.unlink()
        except Exception as E:
            self.add_error("Could not clean up files")

        super().close()

    def is_valid(self):
        return True


class ScriptCrawlerInterface(CrawlerInterface):
    """
    Interface that can be inherited by any browser, browser engine, crawler
    """

    def __init__(self, parser, request, file_name, scraper_name):
        self.parser = parser

        file_name = os.path.relpath(file_name, os.getcwd())

        super().__init__(
            request=request
        )
