import copy
from datetime import datetime, timedelta

from datetime import datetime
from collections import OrderedDict
from webtoolkit import WebLogger, request_to_json


class CrawlItem(object):
    def __init__(self, crawl_id, crawl_type, data=None, crawler_name=None, url=None, request=None):
        self.crawl_id = crawl_id
        self.crawl_type = crawl_type
        self.timestamp = datetime.now()
        self.data = data
        self.crawler_name = crawler_name
        self.url = url
        self.request = request_to_json(request)

    def __str__(self):
        return f"{self.crawl_id} {self.crawl_type} {self.timestamp} {self.crawler_name} {self.url}"


class CrawlerContainer(object):
    """
    Crawl container, history, queue
    """
    CRAWL_TYPE_PING = 0
    CRAWL_TYPE_HEAD = 1
    CRAWL_TYPE_SOCIALDATA = 2
    CRAWL_TYPE_GET = 3

    def __init__(self, time_cache_m=10, records_size=500):
        """
        @param time_cache_m Time window in which results remain in this container
        @param records_size How many records it can store
        """
        self.container = []
        self.records_size = records_size
        self.time_cache_m = time_cache_m
        self.crawl_index = 0

    def crawl(self, crawl_type, crawler_name=None, url=None, request=None) -> int | None:
        """
        Either finds crawl with parameters, or adds new crawl.
        Returns ID of request or None.
        """
        self.expire_old()

        # Try to find existing
        found = self.find(crawl_type, crawler_name=crawler_name, url=url, request=request)
        if found is not None:
            return found

        # Create new request
        self.crawl_index += 1
        crawl_id = self.crawl_index

        item = CrawlItem(
            crawl_id=crawl_id,
            crawl_type=crawl_type,
            crawler_name=crawler_name,
            url=url,
            request=request,
        )
        self.container.append(item)

        if len(self.container) >= self.records_size:
            self.trim_size()

        return crawl_id

    def find(self, crawl_type=None, crawler_name=None, url=None, request=None) -> int | None:
        """
        Finds crawl with parameters. Returns ID or None.
        """
        self.expire_old()

        for item in self.container:
            if self._match(item, crawl_type, crawler_name=crawler_name, url=url, request=request):
                return item.crawl_id
        return None

    def update(self, crawl_id=None, data=None) -> bool:
        """
        Updates results. If crawl_id cannot be found, not updated.
        Returns true if update was successful
        """
        self.expire_old()

        for item in self.container:
            if item.crawl_id == crawl_id:
                item.data = data
                item.timestamp = datetime.now()
                return True
        return False

    def add(self, crawl_type, url, data):
        self.crawl_index += 1

        item = CrawlItem(
            crawl_id=crawl_id,
            crawl_type=crawl_type,
            url=url,
            data=data,
        )

        self.container.append(item)

    def get(self, crawl_id=None, crawl_type=None, crawler_name=None, url=None, request=None) -> CrawlItem | None:
        """Get crawl item by ID if not expired."""
        self.expire_old()

        if not crawl_id:
            crawl_id = self.find(crawl_type=crawl_type,
                      crawler_name=crawler_name,
                      url=url,
                      request=request,)

        if crawl_id:
            for item in self.container:
                if item.crawl_id == crawl_id:
                    return item
        return None

    def leave(self, crawl_id):
        """Remove crawl explicitly."""
        self.container = [c for c in self.container if c.crawl_id != crawl_id]

    def set_time_cache(self, time_cache_m):
        self.time_cache_m = time_cache_m

    def set_records_size(self, row_size):
        self.records_size = row_size

    def get_size(self):
        """Returns size of the container."""
        self.expire_old()
        return len(self.container)

    # ------------------------------
    # Internal helpers
    # ------------------------------

    def expire_old(self):
        """Remove entries older than the time_cache window."""
        cutoff = datetime.now() - timedelta(seconds=self.time_cache_m * 60)
        self.container = [c for c in self.container if c.timestamp >= cutoff]

    def trim_size(self):
        """Enforce the records_size limit."""
        if len(self.container) > self.records_size:
            # drop oldest entries
            overflow = len(self.container) - self.records_size
            self.container = self.container[overflow:]

    def _match(self, item, crawl_type, crawler_name=None, url=None, request=None):
        if not item:
            return False

        if crawler_name and item.crawler_name != crawler_name:
            return False
        if url and item.url != url:
            return False

        input_json_request = request_to_json(request)
        if request and not self.match_requests(item.request, input_json_request):
            return False

        return True

    def match_requests(self, one_request,  two_request):
        if one_request and "crawler_type" in one_request:
            one_request["crawler_type"]=None
        if two_request and "crawler_type" in two_request:
            two_request["crawler_type"]=None
        if one_request and "handler_type" in one_request:
            one_request["handler_type"]=None
        if two_request and "handler_type" in two_request:
            two_request["handler_type"]=None
        if one_request and two_request and one_request == two_request:
            return True

        if one_request is None and two_request is None:
            return True

        return False

    def remove(self, crawl_id):
        """
        return index
        """
        last_found = False

        result = []

        for crawl_data in self.container:
            if crawl_data.crawl_id != crawl_id:
                result.append(crawl_data)
            else:
                last_found = True

        self.container = result

        return last_found
