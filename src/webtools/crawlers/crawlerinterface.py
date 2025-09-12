import json
import os
import base64
from pathlib import Path

from ..webtools import (
    PageRequestObject,
    PageResponseObject,
    WebLogger,
)

from ..ipc import (
    string_to_command,
)

default_user_agent = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:136.0) Gecko/20100101 Firefox/136.0"
)

default_headers = {
    "User-Agent": default_user_agent,
    "Accept": "text/html,application/xhtml+xml,application/xml,application/rss;q=0.9,*/*;q=0.8",
    "Accept-Charset": "utf-8,ISO-8859-1;q=0.7,*;q=0.3",
    "Accept-Encoding": "none",
    "Accept-Language": "en-US,en;q=0.8",
    "Connection": "keep-alive",
}


class CrawlerInterface(object):
    def __init__(self, request=None, url=None, response_file=None, settings=None):
        """
        @param response_file If set, response is stored in a file
        @param settings passed settings
        """
        if not request and url:
            request = PageRequestObject(url)
        elif not request and not url:
            raise TypeError("Incorrect crawler use")

        self.request = request
        self.response = None
        self.response_file = response_file
        self.request_headers = None

        if settings:
            if "settings" not in settings:
                settings["settings"] = {}
            self.set_settings(settings)
        else:
            self.settings = {"settings": {}}

    def set_settings(self, settings):
        self.settings = settings

        if (
            self.settings
            and "headers" in self.settings
            and self.settings["headers"]
            and len(self.settings["headers"]) > 0
        ):
            self.request_headers = self.settings["headers"]
        elif (
            self.request
            and self.request.request_headers
            and len(self.request.request_headers) > 0
        ):
            self.request_headers = self.request.request_headers
        else:
            self.request_headers = default_headers

        real_settings = {}
        if settings and "settings" in settings:
            real_settings = settings["settings"]

        if self.request.timeout_s and "timeout_s" in real_settings:
            self.timeout_s = max(self.request.timeout_s, real_settings["timeout_s"])
        elif self.request.timeout_s:
            self.timeout_s = self.request.timeout_s
        elif "timeout_s" in real_settings:
            self.timeout_s = real_settings["timeout_s"]
        else:
            self.timeout_s = 10

    def set_url(self, url):
        self.request.url = url

    def get_accept_types(self):
        if "settings" not in self.settings:
            return

        accept_string = self.settings["settings"].get("accept_content_types", "all")

        semicolon_index = accept_string.find(";")
        if semicolon_index >= 0:
            accept_string = accept_string[:semicolon_index]

        result = set()
        # Split by comma to separate media types
        media_types = accept_string.split(",")
        for media in media_types:
            # Further split each media type by '/' and '+'
            parts = media.strip().replace("+", "/").split("/")
            for part in parts:
                if part:
                    result.add(part.strip())

        return list(result)

    def run(self):
        """
         - does its job
         - sets self.response
         - clears everything from memory, it created

        if crawler can access web, then should return response (may be invalid)

        @return response, None if feature is not available
        """
        return self.response

    def is_response_valid(self):
        if not self.response:
            return False

        if not self.response.is_valid():
            self.response.add_error(
                f"Response not valid. Status:{self.response.status_code}"
            )
            return False

        content_length = self.response.get_content_length()

        if content_length is not None and "bytes_limit" in self.settings["settings"]:
            if content_length > self.settings["settings"]["bytes_limit"]:
                WebLogger.debug("Page is too big: ".format(content_length))
                self.response.add_error("Page is too big: ".format(content_length))
                return False

        content_type = self.response.get_content_type_keys()
        content_type_keys = self.response.get_content_type_keys()
        if content_type_keys:
            if "all" in self.get_accept_types():
                return True

            match_count = 0
            for item in content_type_keys:
                if item in self.get_accept_types():
                    match_count += 1

            if match_count == 0:
                WebLogger.debug(
                    "Response type is not supported:{}".format(content_type)
                )
                self.response.add_error(
                    "Response type is not supported:{}".format(content_type)
                )
                return False

        return True

    def response_to_bytes(self):
        all_bytes = bytearray()

        if not self.response:
            return all_bytes

        # same as PageResponseObject
        bytes1 = string_to_command("PageResponseObject.__init__", "OK")
        all_bytes.extend(bytes1)
        bytes2 = string_to_command("PageResponseObject.url", self.response.url)
        all_bytes.extend(bytes2)

        if self.response and self.response.request_url:
            thebytes = string_to_command(
                "PageResponseObject.request_url", self.response.request_url
            )
            all_bytes.extend(thebytes)

        bytes4 = string_to_command(
            "PageResponseObject.status_code", str(self.response.status_code)
        )
        all_bytes.extend(bytes4)

        if self.response and self.response.text:
            bytes5 = string_to_command("PageResponseObject.text", self.response.text)
            all_bytes.extend(bytes5)

        bytes6 = string_to_command(
            "PageResponseObject.headers", json.dumps(self.response.headers.headers)
        )
        all_bytes.extend(bytes6)

        bytes7 = string_to_command("PageResponseObject.__del__", "OK")
        all_bytes.extend(bytes7)

        return all_bytes

    def get_response(self):
        return self.response

    def save_response(self):
        if not self.response:
            if self.request:
                WebLogger.error(
                    "Url:{} Have not received response".format(self.request.url)
                )
            else:
                WebLogger.error("Have not received response")
            return False

        if self.response_file:
            self.save_response_file(self.response_file)

        if self.settings and "remote_server" in self.settings:
            self.save_response_remote(self.settings["remote_server"])

        return True

    def save_response_file(self, file_name):
        if not file_name:
            return

        all_bytes = self.response_to_bytes()

        path = Path(self.response_file)
        if not path.parent.exists():
            path.parent.mkdir(parents=True, exist_ok=True)

        with open(self.response_file, "wb") as fh:
            fh.write(all_bytes)

    def save_response_remote(self, remote_server):
        import requests

        if not self.response:
            return

        raw_content = self.response.get_text()
        if raw_content:
            raw_content_bytes = raw_content.encode(
                self.response.encoding or "utf-8", errors="replace"
            )
            encoded_content = base64.b64encode(raw_content_bytes).decode("ascii")
        else:
            encoded_content = ""

        payload = {}
        payload["url"] = self.response.url
        payload["request_url"] = self.response.request_url
        payload["Contents"] = encoded_content
        payload["Headers"] = self.response.get_headers()
        payload["status_code"] = self.response.status_code
        payload["crawler_data"] = self.settings

        try:
            response = requests.post(remote_server + "/set", json=payload)

            if response.status_code == 200:
                print("Response successfully sent to the remote server.")
                return response.json()  # Assuming the server responds with JSON
            else:
                print(f"Failed to send response. Status code: {response.status_code}")
                print(f"Response text: {response.text}")
                return None
        except requests.RequestException as E:
            # Handle any exceptions raised by the requests library
            print(f"An error occurred while sending the response: {E}")
            return None
        except TypeError as E:
            print("Cannot post payload\n{}".format(payload))
            return None

    def is_valid(self):
        return False

    def close(self):
        pass

    def get_main_path(self):
        file_path = os.path.realpath(__file__)
        full_path = Path(file_path)
        return full_path.parents[3]

    def get_request_headers(self):
        if self.request_headers:
            return self.request_headers

        return default_headers

    def get_request_headers_default():
        return default_headers

    def get_user_agent():
        return default_user_agent
