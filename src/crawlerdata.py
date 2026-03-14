import os
import json
from webtoolkit import WebLogger, json_to_request
from src.webtools import WebConfig, ScriptCrawler, Url, RequestBuilder

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

        page_request = self.get_request_data_from_flask_request()
        if not page_request:
            WebLogger.error(
                "Url:{} Cannot obtain page request".format(url)
            )
            return

        page_request = RequestBuilder.update_request(page_request)
        page_request = self.fill_crawler_data(page_request)

        # important for crawl to be full of precise information
        # we will be searching using crawler_name and handler_name
        # without this information we might find something we do not want

        if page_request and page_request.handler_name is None:
            url = Url(request=page_request)
            handler = url.get_handler()
            if handler is not None:
                page_request.handler_name = handler.__class__.__name__

        if not page_request:
            WebLogger.error(
                "Url:{} Cannot run request without crawler".format(url)
            )
            return

        return page_request

    def get_request_data_from_flask_request(self):
        if "crawler_data" in self.request.args:
            data_str = self.request.args.get("crawler_data")
            data_json = json.loads(data_str)
            data_json["url"] = self.request.args.get("url")
            page_request = json_to_request(data_json)
        else:
            page_request = json_to_request(self.request.args)

        if page_request.crawler_name == "":
            page_request.crawler_name = None
        if page_request.handler_name == "":
            page_request.handler_name = None

        return page_request

    def fill_crawler_data(self, page_request):
        """
        Override settings from third what is specified in configuration
        """
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

        http_proxy = os.environ.get("http_proxy")
        if http_proxy:
            page_request.http_proxy = http_proxy
        https_proxy = os.environ.get("https_proxy")
        if https_proxy:
            page_request.https_proxy = https_proxy
        http_proxy = os.environ.get("HTTP_PROXY")
        if http_proxy:
            page_request.http_proxy = http_proxy
        https_proxy = os.environ.get("HTTPS_PROXY")
        if https_proxy:
            page_request.https_proxy = https_proxy

        return page_request
