from datetime import datetime
from collections import OrderedDict
from rsshistory import webtools
from rsshistory.configuration import Configuration


class CrawlerInfo(object):

    def __init__(self):
        self.queue = OrderedDict()
        self.crawl_index = 0

    def enter(self, url):
        self.queue[self.crawl_index] = datetime.now(), url

        if self.get_size() > 100:
            self.queue = OrderedDict()

        self.crawl_index += 1
        return self.crawl_index -1

    def leave(self, crawl_index):
        if crawl_index in self.queue:
            del self.queue[crawl_index]

    def get_size(self):
        return len(self.queue)


class Crawler(object):
    def __init__(self):
        self.crawler_info = CrawlerInfo()

    def run(self, url, crawler_data = None):
        page_url = self.get_page_url(url, crawler_data)

        request_headers = crawler_data["settings"]["headers"]
        request_ping = crawler_data["settings"]["ping"]
        full = crawler_data["settings"]["full"]

        if request_headers:
            # TODO implement
            headers = page_url.get_headers()
            all_properties = [
                    { "name" : "Headers",
                      "data" : headers }
            ]
        elif request_ping:
            # TODO implement
            headers = page_url.get_headers()
            all_properties = [
                    { "name" : "Headers",
                      "data" : headers }
            ]
        else:
            # TODO what if there is exception
            crawl_index = self.crawler_info.enter(url)

            response = page_url.get_response()

            try:
                all_properties = page_url.get_properties(full=True, include_social=full)
                self.crawler_info.leave(crawl_index)
            except Exception as e:
                self.crawler_info.leave(crawl_index)
                raise

        return all_properties

    def get_page_url(self, url, crawler_data):
        page_url = webtools.Url(url)
        options = page_url.get_init_page_options()

        remote_server = crawler_data["settings"]["remote_server"]

        new_mapping = None

        config = Configuration()

        if "crawler" not in crawler_data and "name" in crawler_data:
            new_mapping = config.get_crawler(name = crawler_data["name"])
        elif "name" not in crawler_data and "crawler" in crawler_data:
            new_mapping = config.get_crawler(crawler_name = crawler_data["crawler"])
        elif "name" not in crawler_data and "crawler" not in crawler_data:
            pass
        else:
            new_mapping = crawler_data
            new_mapping["crawler"] = webtools.WebConfig.get_crawler_from_string(new_mapping["crawler"])

        if new_mapping:
            if new_mapping["settings"] is None:
                new_mapping["settings"] = {}
            new_mapping["settings"]["remote-server"] = remote_server

            print("Running:{}, with:{}".format(url, new_mapping))

            options.mode_mapping = [new_mapping]

        handler_class = None
        if "handler_class" in crawler_data:
            handler_class = Url.get_handler_by_name(crawler_data["handler_class"])

        page_url = webtools.Url(url, page_options=options, handler_class = handler_class)

        return page_url
