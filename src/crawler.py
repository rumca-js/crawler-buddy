import subprocess
import psutil
import json
from datetime import datetime
from collections import OrderedDict
from src import webtools
from src.configuration import Configuration
from src.entryrules import EntryRules
from src import CrawlHistory


class CrawlerInfo(object):

    def __init__(self):
        self.queue = OrderedDict()
        self.crawl_index = 0

    def enter(self, url, crawler_data=None):
        self.queue[self.crawl_index] = datetime.now(), url, crawler_data

        if self.get_size() > 100:
            self.queue = OrderedDict()

        self.crawl_index += 1
        return self.crawl_index - 1

    def leave(self, crawl_index):
        if crawl_index in self.queue:
            del self.queue[crawl_index]

    def get_size(self):
        return len(self.queue)


class Crawler(object):
    def __init__(self):
        self.crawler_info = CrawlerInfo()
        self.entry_rules = EntryRules()
        self.configuration = Configuration()
        self.url_history = CrawlHistory(200)

    def get_history(self):
        return self.url_history

    def get_request_data(self, request):
        """
        Reads data from request
        """
        url = request.args.get("url")

        crawler_data = self.get_request_data_from_request(request)
        crawler_data = self.fill_crawler_data(url, crawler_data)
        crawler_data = self.get_crawler(url, crawler_data)

        if not crawler_data:
            webtools.WebLogger.error(
                "Url:{} Cannot run request without crawler".format(url)
            )
            return

        return crawler_data

    def get_request_data_from_request(self, request):
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
            crawler_data["settings"]["remote_server"] = "http://" + host + ":" + str(port)

        crawler_data["headers"] = headers

        return crawler_data

    def fill_crawler_data(self, url, crawler_data):
        if "ssl_verify" not in crawler_data["settings"] and self.configuration.is_set(
            "ssl_verify"
        ):
            crawler_data["settings"]["ssl_verify"] = True
        if "respect_robots_txt" not in crawler_data[
            "settings"
        ] and self.configuration.is_set("respect_robots_txt"):
            crawler_data["settings"]["respect_robots_txt"] = True

        if "bytes_limit" not in crawler_data and self.configuration.is_set(
            "bytes_limit"
        ):
            crawler_data["settings"]["bytes_limit"] = self.configuration.get(
                "bytes_limit"
            )
        else:
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

    def get_crawl_properties(self, url, crawler_data):
        """
        returns properties
        """
        name = None
        if "name" in crawler_data:
            name = crawler_data["name"]
        crawler = None
        if "crawler" in crawler_data:
            crawler = crawler_data["crawler"]

        things = self.get_history().find(url=url, crawler_name=name, crawler=crawler)

        if things:
            print("Returning from saved properties")
            index, timestamp, all_properties = things

            if all_properties:
                return all_properties

        all_properties = self.run(url, crawler_data)

        if all_properties:
            self.get_history().add((url, all_properties))
        else:
            all_properties = self.get_history().find(url=url)

        return all_properties

    def run(self, url, crawler_data=None):
        if not crawler_data:
            webtools.WebLogger.error(
                "Url:{} Cannot run request without crawler_data".format(url)
            )
            return

        page_url = self.get_page_url(url, crawler_data)

        if not page_url:
            webtools.WebLogger.error(
                "Could not create page url for {} {}".format(url, crawler_data)
            )
            return

        request_headers = crawler_data["settings"]["headers"]
        request_ping = crawler_data["settings"]["ping"]
        full = crawler_data["settings"]["full"]

        if request_headers:
            # TODO implement
            headers = page_url.get_headers()
            all_properties = [{"name": "Headers", "data": headers}]
        elif request_ping:
            # TODO implement
            headers = page_url.get_headers()
            all_properties = [{"name": "Headers", "data": headers}]
        else:
            # TODO what if there is exception
            crawl_index = self.crawler_info.enter(url, crawler_data)

            try:
                response = page_url.get_response()
                all_properties = page_url.get_properties(full=True, include_social=full)
                self.crawler_info.leave(crawl_index)
            except Exception as e:
                self.crawler_info.leave(crawl_index)
                raise

        if webtools.WebConfig.count_chrom_processes() > 30:
            webtools.WebLogger.error("Too many chrome processes")
            webtools.WebConfig.kill_chrom_processes()

        return all_properties

    def get_page_url(self, url, crawler_data):
        """ """

        print("Running:{}, with:{}".format(url, crawler_data))

        page_url = webtools.Url(url, settings=crawler_data)
        return page_url

    def get_default_crawler(self, url):
        default_crawler = self.configuration.get("default_crawler")
        if default_crawler:
            new_mapping = self.configuration.get_crawler(name=default_crawler)
            if new_mapping:
                return new_mapping

        new_mapping = webtools.WebConfig.get_default_crawler(url)
        if new_mapping:
            return new_mapping
