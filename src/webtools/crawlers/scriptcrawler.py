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

    def run(self):
        if not self.is_valid():
            return

        remote_server = self.request.settings.get("remote_server")

        if remote_server:
            return self.run_via_server(remote_server)
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

        WebLogger.debug("Running CWD:{} via server with script:{}".format(self.cwd, script))

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
            self.response.add_error("Incorrect script call: {}".format(str(E)))
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
            self.response.add_error("Return code invalid: {}".format(p.returncode))

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
            self.response = PageResponseObject(
                self.request.url,
                text=None,
                status_code=HTTP_STATUS_CODE_SERVER_ERROR,
                request_url=self.request.url,
            )

            WebLogger.error(
                f"Url:{self.request.url}: Failed to fetch data. Status code: {response.status_code}"
            )
            self.response.add_error("Failed to fetch data")

    def run_via_file(self):
        self.response = PageResponseObject(
            self.request.url,
            text=None,
            status_code=HTTP_STATUS_CODE_SERVER_ERROR,
            request_url=self.request.url,
        )

        response_file_location = Path(self.get_response_file())
        WebLogger.debug("Running via file {}".format(response_file_location))

        if len(response_file_location.parents) > 1:
            response_dir = response_file_location.parents[0]
            WebLogger.debug(str(response_dir))
            if not response_dir.exists():
                response_dir.mkdir(parents=True, exist_ok=True)

        if response_file_location.exists():
            response_file_location.unlink()

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
            WebLogger.error(
                "Url:{}. Script:'{}'. Return code invalid:{}. Path:{}".format(
                    self.request.url,
                    script,
                    p.returncode,
                    self.cwd,
                )
            )
            self.response.add_error("Return code invalid: {}".format(p.returncode))

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

            self.response = PageResponseObject(
                self.request.url,
                text=None,
                status_code=HTTP_STATUS_CODE_SERVER_ERROR,
                request_url=self.request.url,
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
            self.response.add_error("Operating path does not exist: {}".format(operating_path))
            return

        return operating_path

    def close(self):
        response_file = self.get_response_file()
        if response_file:
            response_file_location = Path(response_file)
            if response_file_location.exists():
                response_file_location.unlink()

        super().close()

    def is_valid(self):
        if not self.script:
            return False

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
