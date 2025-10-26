import json
from webtoolkit import WebLogger, json_to_request
from src.webtools import WebConfig

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

        page_request = self.get_request_data_from_request()
        if not page_request:
            WebLogger.error(
                "Url:{} Cannot obtain page request".format(url)
            )
            return

        page_request = self.fill_crawler_data(url, page_request)
        page_request = self.get_crawler(url, page_request)

        if not page_request:
            WebLogger.error(
                "Url:{} Cannot run request without crawler".format(url)
            )
            return

        return page_request

    def get_request_data_from_request(self):
        if "crawler_data" in self.request.args:
            data_str = self.request.args.get("crawler_data")
            data_json = json.loads(data_str)
            data_json["url"] = self.request.args.get("url")
            page_request = json_to_request(data_json)
        else:
            page_request = json_to_request(self.request.args)

        return page_request

    def fill_crawler_data(self, url, page_request):
        """
        order: 
         - first what is specified by args
         - second what is specified by browser config (json file)
         - third what is specified in configuration
        """
        new_mapping = self.configuration.get_crawler(name=page_request.crawler_name)
        if new_mapping:
            new_mapping = new_mapping

            if new_mapping:
                page_request = self.settings_to_request(page_request, new_mapping)

        if page_request.ssl_verify is None:
            page_request.ssl_verify = self.configuration.get("ssl_verify")
        if page_request.respect_robots is None:
            page_request.respect_robots = self.configuration.get("respect_robots_txt")
        if page_request.bytes_limit is None:
            page_request.bytes_limit = self.configuration.get("bytes_limit")

        if page_request.bytes_limit is None:
            page_request.bytes_limit = WebConfig.get_bytes_limit()
        if page_request.accept_types is None:
            page_request.accept_types = "all"

        return page_request

    def settings_to_request(self, page_request, crawler_settings):
        def set_property_if_none(page_request, setting_name, crawler_settings, key_in_settings):
            if getattr(page_request, setting_name) is None:
                setting_value = crawler_settings.get("settings", {}).get(key_in_settings)
                if setting_value is not None:
                    setattr(page_request, setting_name, setting_value)

        settings = crawler_settings.get("settings", {})
        set_property_if_none(page_request, 'user_agent', settings, 'User-Agent')
        set_property_if_none(page_request, 'request_headers', settings, 'request_headers')
        set_property_if_none(page_request, 'timeout_s', settings, 'timeout_s')
        set_property_if_none(page_request, 'delay_s', settings, 'delay_s')
        set_property_if_none(page_request, 'ssl_verify', settings, 'ssl_verify')
        set_property_if_none(page_request, 'respect_robots', settings, 'respect_robots_txt')
        set_property_if_none(page_request, 'bytes_limit', settings, 'bytes_limit')
        set_property_if_none(page_request, 'accept_types', settings, 'accepte_types')

        return page_request

    def get_crawler(self, url, page_request):
        name = None

        if page_request.crawler_name:
            name = page_request.crawler_name
        else:
            name = self.get_default_crawler_name(url)
            if not name:
                return

        if not name:
            WebLogger.error("Could not find crawler")
            return

        crawler = WebConfig.get_crawler_from_string(name)
        if not crawler:
            WebLogger.error(f"Could not find crawler {name}")
            return

        page_request.crawler_type = crawler(url=url)

        return page_request

    def get_default_crawler_name(self, url):
        crawler_name = self.entry_rules.get_browser(url)
        new_mapping = self.configuration.get_crawler(name=crawler_name)
        if new_mapping:
            return new_mapping["name"]

        default_crawler = self.configuration.get("default_crawler")
        if default_crawler:
            new_mapping = self.configuration.get_crawler(name=default_crawler)
            if new_mapping:
                return new_mapping["name"]

        new_mapping = WebConfig.get_default_crawler(url)
        if new_mapping:
            return new_mapping["name"]
