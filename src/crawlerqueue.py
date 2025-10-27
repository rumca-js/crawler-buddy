from datetime import datetime
from collections import OrderedDict
from webtoolkit import WebLogger


class CrawlerQueue(object):

    def __init__(self, max_queue_size=10):
        self.queue = OrderedDict()
        self.crawl_index = 0
        self.max_queue_size = max_queue_size

    def get_size(self):
        return len(self.queue)

    def enter(self, url, crawler_data=None):
        if self.get_size() > self.max_queue_size:
            WebLogger.error("Crawler info too many requests")
            return

        if self.find(url, crawler_data):
            return

        self.queue[self.crawl_index] = datetime.now(), url, crawler_data

        self.crawl_index += 1
        return self.crawl_index - 1

    def find(self, input_url=None, input_crawler_data=None):
        found_crawler = False
        found_url = False

        for index, stored_data in self.queue.items():
            datetime, url, crawler_data = stored_data

            if input_url == url:
                found_url = True

            if input_crawler_data and crawler_data and input_crawler_data.crawler_name == crawler_data.crawler_name:
                found_crawler = True

            if input_url and input_crawler_data:
                if found_url and found_crawler:
                    return True
            elif input_url and found_url:
                return True
            elif input_crawler_data and found_crawler:
                return True;

        return False

    def leave(self, crawl_index):
        if crawl_index in self.queue:
            del self.queue[crawl_index]

    def get_size(self):
        return len(self.queue)
