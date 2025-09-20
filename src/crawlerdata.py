import json
from src import webtools
from src.entryrules import EntryRules


class CrawlerData(object):
    def __init__(self, configuration, request=None):
        self.request = request
        self.configuration = configuration
        self.entry_rules = EntryRules()

    def set_request(self, request):
        self.request = request

    def get_request_data(self):
        """
        Reads data from request
        """
        url = self.request.args.get("url")

        crawler_data = self.get_request_data_from_request()
        crawler_data = self.fill_crawler_data(url, crawler_data)
        crawler_data = self.get_crawler(url, crawler_data)

        if not crawler_data:
            webtools.WebLogger.error(
                "Url:{} Cannot run request without crawler".format(url)
            )
            return

        return crawler_data

    def get_request_data_from_request(self):
        request = self.request

        crawler_data = request.args.get("crawler_data")
        crawler = request.args.get("crawler")
        name = request.args.get("name")
        headers = request.args.get("headers")

        if crawler_data:
            try:
                crawler_data = json.loads(crawler_data)
            except json.JSONDecodeError as E:
                print(str(E))

        if crawler_data is None:
            crawler_data = {}

        if crawler:
            crawler_data["crawler"] = crawler
        if name:
            crawler_data["name"] = name

        if "settings" not in crawler_data:
            crawler_data["settings"] = {}

        crawler_data["settings"]["full"] = request.args.get("full")
        crawler_data["settings"]["headers"] = request.args.get("headers")
        crawler_data["settings"]["ping"] = request.args.get("ping")

        # TODO host is 0.0.0.0 because we want to listen to "any".
        # host = self.configuration.get("host")
        # here - we want to report back to crawler server with results
        host = "127.0.0.1"
        port = self.configuration.get("port")

        if "remote_server" not in crawler_data["settings"]:
            crawler_data["settings"]["remote_server"] = (
                "http://" + host + ":" + str(port)
            )

        crawler_data["headers"] = headers

        return crawler_data

    def fill_from_config(self, crawler_data, aproperty):
        if aproperty not in crawler_data["settings"]:
            if self.configuration.is_set(aproperty):
                crawler_data["settings"][aproperty] = self.configuration.get(aproperty)

    def fill_crawler_data(self, url, crawler_data):
        self.fill_from_config(crawler_data, "ssl_verify")
        self.fill_from_config(crawler_data, "respect_robots_txt")
        self.fill_from_config(crawler_data, "bytes_limit")

        if crawler_data["settings"].get("bytes_limit") is None:
            crawler_data["settings"][
                "bytes_limit"
            ] = webtools.WebConfig.get_bytes_limit()

        if "accept_content_types" not in crawler_data["settings"]:
            crawler_data["settings"]["accept_content_types"] = "all"

        return crawler_data

    def get_crawler(self, url, crawler_data):
        remote_server = crawler_data["settings"]["remote_server"]

        new_mapping = None

        if "crawler" not in crawler_data and "name" in crawler_data:
            new_mapping = self.configuration.get_crawler(name=crawler_data["name"])
            if not new_mapping:
                return
            new_mapping["crawler"] = new_mapping["crawler"](url=url)
        elif "name" not in crawler_data and "crawler" in crawler_data:
            new_mapping = self.configuration.get_crawler(
                crawler_name=crawler_data["crawler"]
            )
            if not new_mapping:
                return
            new_mapping["crawler"] = new_mapping["crawler"](url=url)
        elif "name" not in crawler_data and "crawler" not in crawler_data:
            crawler_name = self.entry_rules.get_browser(url)
            if not crawler_name:
                new_mapping = self.get_default_crawler(url)
                if not new_mapping:
                    return
            else:
                new_mapping = self.configuration.get_crawler(name=crawler_name)
                if not new_mapping:
                    webtools.WebLogger.error(
                        "Cannot find specified crawler in config: {}".format(
                            crawler_name
                        )
                    )
                new_mapping["crawler"] = new_mapping["crawler"](url=url)
        else:
            new_mapping = self.configuration.get_crawler(name=crawler_data["name"])
            if not new_mapping:
                return
            new_mapping["crawler"] = new_mapping["crawler"](url=url)

        if not new_mapping:
            webtools.WebLogger.error("Could not find crawler")
            return

        # use what is not default by crawler buddy
        for key in crawler_data:
            if key != "settings" and key not in new_mapping:
                new_mapping[key] = crawler_data[key]

        for key in crawler_data["settings"]:
            new_mapping["settings"][key] = crawler_data["settings"][key]

        if new_mapping["settings"] is None:
            new_mapping["settings"] = {}
        new_mapping["settings"]["remote_server"] = remote_server

        if "handler_class" in new_mapping:
            new_mapping["handler_class"] = Url.get_handler_by_name(
                new_mapping["handler_class"]
            )

        return new_mapping

    def get_crawler(self, url, crawler_data):
        remote_server = crawler_data["settings"]["remote_server"]

        new_mapping = None

        if "crawler" not in crawler_data and "name" in crawler_data:
            new_mapping = self.configuration.get_crawler(name=crawler_data["name"])
            if not new_mapping:
                return
            new_mapping["crawler"] = new_mapping["crawler"](url=url)
        elif "name" not in crawler_data and "crawler" in crawler_data:
            new_mapping = self.configuration.get_crawler(
                crawler_name=crawler_data["crawler"]
            )
            if not new_mapping:
                return
            new_mapping["crawler"] = new_mapping["crawler"](url=url)
        elif "name" not in crawler_data and "crawler" not in crawler_data:
            crawler_name = self.entry_rules.get_browser(url)
            if not crawler_name:
                new_mapping = self.get_default_crawler(url)
                if not new_mapping:
                    return
            else:
                new_mapping = self.configuration.get_crawler(name=crawler_name)
                if not new_mapping:
                    webtools.WebLogger.error(
                        "Cannot find specified crawler in config: {}".format(
                            crawler_name
                        )
                    )
                new_mapping["crawler"] = new_mapping["crawler"](url=url)
        else:
            new_mapping = self.configuration.get_crawler(name=crawler_data["name"])
            if not new_mapping:
                return
            new_mapping["crawler"] = new_mapping["crawler"](url=url)

        if not new_mapping:
            webtools.WebLogger.error("Could not find crawler")
            return

        # use what is not default by crawler buddy
        for key in crawler_data:
            if key != "settings" and key not in new_mapping:
                new_mapping[key] = crawler_data[key]

        for key in crawler_data["settings"]:
            new_mapping["settings"][key] = crawler_data["settings"][key]

        if new_mapping["settings"] is None:
            new_mapping["settings"] = {}
        new_mapping["settings"]["remote_server"] = remote_server

        if "handler_class" in new_mapping:
            new_mapping["handler_class"] = Url.get_handler_by_name(
                new_mapping["handler_class"]
            )

        return new_mapping

    def get_default_crawler(self, url):
        default_crawler = self.configuration.get("default_crawler")
        if default_crawler:
            new_mapping = self.configuration.get_crawler(name=default_crawler)
            if new_mapping:
                return new_mapping

        new_mapping = webtools.WebConfig.get_default_crawler(url)
        if new_mapping:
            return new_mapping
