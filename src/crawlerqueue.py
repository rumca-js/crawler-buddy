from datetime import datetime
from collections import OrderedDict
from src import webtools


class CrawlerQueue(object):

    def __init__(self, max_queue_size=10):
        self.queue = OrderedDict()
        self.crawl_index = 0
        self.max_queue_size = max_queue_size

    def get_size(self):
        return len(self.queue)

    def enter(self, url, crawler_data=None):
        if self.get_size() > self.max_queue_size:
            webtools.WebLogger.error("Crawler info too many requests")
            return

        if self.find(url, crawler_data):
            return

        self.queue[self.crawl_index] = datetime.now(), url, crawler_data

        self.crawl_index += 1
        return self.crawl_index - 1

    def find(self, input_url=None, input_crawler_data=None):
        for index, stored_data in self.queue.items():
            datetime, url, crawler_data = stored_data
            if input_url == url and input_crawler_data == crawler_data:
                return True

        return False

    def leave(self, crawl_index):
        if crawl_index in self.queue:
            del self.queue[crawl_index]

    def get_size(self):
        return len(self.queue)
