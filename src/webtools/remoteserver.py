import json
import requests
import urllib.parse
import base64
from .webtools import (
    PageResponseObject,
    HTTP_STATUS_TOO_MANY_REQUESTS,
    json_to_response,
)


class RemoteServer(object):
    """
    Crawler buddy communication class
    """

    def __init__(self, remote_server, timeout_s=30):
        self.remote_server = remote_server
        self.timeout_s = timeout_s

    def get_getj(self, url, name="", settings=None):
        """
        @returns None in case of error
        """
        url = url.strip()
        encoded_url = urllib.parse.quote(url, safe="")

        link = self.remote_server
        link = f"{link}/getj"

        args = None

        if settings:
            if name != "":
                settings["name"] = name

            crawler = settings.get("crawler", None)
            if crawler:
                settings["crawler"] = str(crawler)

            try:
                crawler_data = json.dumps(settings)
            except Exception as E:
                print("Cannot json serialize:{}".format(settings))
                raise

            encoded_crawler_data = urllib.parse.quote(crawler_data, safe="")

            args = f"crawler_data={encoded_crawler_data}"
        elif name != "":
            args = f"name={name}"

        return self.perform_remote_call(
            link_call=link, url=url, settings=settings, args=args
        )

    def get_feedsj(self, url, settings=None):
        """
        @returns None in case of error
        """

        link = self.remote_server
        link = f"{link}/feedsj"

        return self.perform_remote_call(link, url, settings)

    def get_socialj(self, url, settings=None):
        """
        @returns None in case of error
        """

        link = self.remote_server
        link = f"{link}/socialj"

        return self.perform_remote_call(link, url, settings)

    def get_pingj(self, url, settings=None):
        """
        @returns None in case of error
        """

        link = self.remote_server
        link = f"{link}/pingj"

        json = self.perform_remote_call(link, url, settings)
        if json:
            return json.get("status")

    def perform_remote_call(self, link_call, url, settings=None, args=None):
        """
        @param link_call Remote server endpoint
        @param url Url for which we call Remote server
        """
        url = url.strip()
        encoded_url = urllib.parse.quote(url, safe="")

        link_call = f"{link_call}?url={encoded_url}"

        if args:
            link_call = f"{link_call}&{args}"

        text = None

        timeout_s = 50
        if settings:
            if "settings" in settings:
                real_settings = settings.get("settings", {})
                timeout_s = real_settings.get("timeout_s", 50)
                timeout_s += real_settings.get("delay_s", 0)
                timeout_s += 5

        print(f"Remote server: Calling {link_call}")

        try:
            with requests.get(url=link_call, timeout=timeout_s, verify=False) as result:
                if result.status_code == HTTP_STATUS_TOO_MANY_REQUESTS:
                    return

                text = result.text
        except Exception as E:
            print("Remote error. " + str(E))
            return

        if not text:
            print("Remote error. No text")
            return

        # print("Calling:{}".format(link))

        json_obj = None
        try:
            json_obj = json.loads(text)
        except ValueError as E:
            print("Url:{} Remote error. Cannot read response".format(link_call, text))
            # WebLogger.error(info_text="Url:{} Cannot read response".format(link_call), detail_text=text)
            return
        except TypeError as E:
            print("Url:{} Remote error. Cannot read response".format(link_call, text))
            # WebLogger.error(info_text="Url:{} Cannot read response".format(link_call), detail_text=text)
            return

        if "success" in json_obj and not json_obj["success"]:
            print("Url:{} Remote error. Not a success".format(link_call))
            # WebLogger.error(json_obj["error"])
            return False

        return json_obj

    def get_properties(self, url, name="", settings=None):
        json_obj = self.get_getj(url=url, name=name, settings=settings)

        if json_obj:
            return self.read_properties_section("Properties", json_obj)

        return json_obj

    def read_properties_section(self, section_name, all_properties):
        if not all_properties:
            return

        if "success" in all_properties and not all_properties["success"]:
            # print("Url:{} Remote error. Not a success".format(link))
            print("Remote error. Not a success")
            # WebLogger.error(all_properties["error"])
            return False

        for properties in all_properties:
            if section_name == properties["name"]:
                return properties["data"]

    def unpack_data(self, input_data):
        """
        TODO remove?
        """
        json_data = {}

        data = json.loads(input_data)

        response = self.read_properties_section("Response", data)
        contents_data = self.read_properties_section("Contents", data)

        if response:
            json_data["status_code"] = response["status_code"]
        if contents_data:
            json_data["contents"] = contents_data["Contents"]
        if response:
            json_data["Content-Length"] = response["Content-Length"]
        if response:
            json_data["Content-Type"] = response["Content-Type"]

        return json_data

    def get_response(self, all_properties):
        properties = self.read_properties_section("Properties", all_properties)
        response_data = self.read_properties_section("Response", all_properties)

        text_data = self.read_properties_section("Text", all_properties)
        binary_data = self.read_properties_section("Binary", all_properties)

        text = ""
        if text_data:
            text = text_data["Contents"]

        binary = None
        if binary_data:
            if binary_data["Contents"]:
                binary = binary_data["Contents"]

        if not response_data:
            o = PageResponseObject(url=properties["link"], text=text, binary=binary)
            return o

        response = json_to_response(response_data)
        response.text = text
        response.binary = binary

        url = properties["link"]

        return response
