import json
import requests


class RemoteServer(object):
    """
    Crawler buddy communication class
    """
    def __init__(self, remote_server, timeout_s=30):
        self.remote_server = remote_server
        self.timeout_s = timeout_s

    def get_social(self, url, settings=None):
        """
        @returns None in case of error
        """

        encoded_url = urllib.parse.quote(url, safe="")

        if settings:
            crawler_data = json.dumps(settings)
            encoded_crawler_data = urllib.parse.quote(crawler_data, safe="")

            link = self.remote_server
            link = f"{link}/socialj?url={encoded_url}&crawler_data={encoded_crawler_data}"
            print("RemoteServer: calling:{}".format(link))
        else:
            link = self.remote_server
            link = f"{link}/socialj?url={encoded_url}"
            print("RemoteServer: calling:{}".format(link))

        timeout_s = 50
        if settings and "timeout_s" in settings:
            timeout_s = settings["timeout_s"]

        # we make request longer - for the server to be able to respond in time
        timeout_s += 5

        text = None
        try:
            with requests.get(url=link, timeout=timeout_s, verify=False) as result:
                text = result.text
        except Exception as E:
            return

        if not text:
            return

        print("Calling:{}".format(link))

        json_obj = None
        try:
            json_obj = json.loads(text)
        except ValueError as E:
            # WebLogger.error(info_text="Url:{} Cannot read response".format(link), detail_text=text)
            return
        except TypeError as E:
            # WebLogger.error(info_text="Url:{} Cannot read response".format(link), detail_text=text)
            return

        if "success" in json_obj and not json_obj["success"]:
            # WebLogger.error(json_obj["error"])
            return False

        return json_obj

    def get_crawlj(self, url, name="", settings=None):
        """
        @returns None in case of error
        """
        import requests

        encoded_url = urllib.parse.quote(url, safe="")

        if settings:
            if name != "":
                settings["name"] = name

            crawler_data = json.dumps(settings)
            encoded_crawler_data = urllib.parse.quote(crawler_data, safe="")

            link = self.remote_server
            link = f"{link}/crawlj?url={encoded_url}&crawler_data={encoded_crawler_data}"
            # WebLogger.debug("RemoteServer: calling:{}".format(link))
        elif name != "":
            link = self.remote_server
            link = f"{link}/crawlj?url={encoded_url}&name={name}"

            # WebLogger.debug("RemoteServer: calling:{}".format(link))
        else:
            link = self.remote_server
            link = f"{link}/crawlj?url={encoded_url}"

            # WebLogger.debug("RemoteServer: calling:{}".format(link))

        timeout_s = 50
        if settings and "timeout_s" in settings:
            timeout_s = settings["timeout_s"]

        # we make request longer - for the server to be able to respond in time
        timeout_s += 5

        text = None
        try:
            with requests.get(url=link, timeout=timeout_s, verify=False) as result:
                text = result.text
        except Exception as E:
            return

        if not text:
            return

        json_obj = None
        try:
            json_obj = json.loads(text)
        except ValueError as E:
            # WebLogger.error(info_text="Url:{} Cannot read response".format(link), detail_text=text)
            return
        except TypeError as E:
            # WebLogger.error(info_text="Url:{} Cannot read response".format(link), detail_text=text)
            return

        if "success" in json_obj and not json_obj["success"]:
            # WebLogger.error(json_obj["error"])
            return False

        return json_obj

    def get_properties(self, url, name = "", settings=None):
        json_obj = self.crawlj(url=url, name=name, settings=settings)

        if json_obj:
            return self.read_properties_section("Properties", json_obj)

        return json_obj

    def read_properties_section(self, section_name, all_properties):
        if not all_properties:
            return

        if "success" in all_properties and not all_properties["success"]:
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
