

class CrawlerPool(object):
    pool = None
    def get():
        if CrawlerPool.pool is None:
            CrawlerPool.pool = CrawlerPool()

        return CrawlerPool.pool

    def get(crawler):
        if CrawlerPool.pool is None:
            CrawlerPool.pool = CrawlerPool()

        pool = CrawlerPool.pool

        if crawler not in pool:
            pool[crawler] = {}

        return pool[crawler]

    def __init__(self):
        self.crawlers = {}

    def set(self, crawler, key, value):
        if crawler not in self.crawlers:
            self.crawlers[crawler] = {}

        self.crawlers[crawler][key] = value

    def get(self, crawler, key):
        if crawler not in self.crawlers:
            self.crawlers[crawler] = {}

        if key in self.crawlers[crawler]:
            return self.crawlers[crawler][key]
