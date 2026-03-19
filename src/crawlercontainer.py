from datetime import datetime, timedelta
import threading

from datetime import datetime
from collections import OrderedDict
from webtoolkit import WebLogger, request_to_json, copy_request
from src.webtools import WebConfig


class CrawlItem(object):
    def __init__(self, crawl_id, crawl_type, request, data=None):
        self.crawl_id = crawl_id
        self.crawl_type = crawl_type
        self.timestamp = datetime.now()
        self.data = data
        self.request = request_to_json(request)

        self.request_real = copy_request(request)

    def __str__(self):
        data = "No"
        if self.data is not None:
            data = "Yes"
        return f"{self.crawl_id} {self.crawl_type} {self.timestamp} {self.crawler_name} {self.url} Data:{data}"

    def get_url(self):
        return self.request_real.url

    def is_response(self):
        return self.data is not None

    def is_expired(self):
        """
        Elements with data, that are in queue are not expired
        """
        """
        if not self.is_response():
            return False

        timeout_s = WebConfig.get_default_timeout_s()
        if self.request_real:
            timeout_s = self.request_real.timeout_s

        if timeout_s > 0:
            return datetime.now() > self.timestamp + timedelta(seconds=timeout_s)
        """
        return False


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
        self.lock = threading.Lock()           # protects running_ids
        self.no_history_crawls = 0

    def crawl_type_to_str(crawl_type):
        if crawl_type == CrawlerContainer.CRAWL_TYPE_PING:
            return "Ping"
        if crawl_type == CrawlerContainer.CRAWL_TYPE_HEAD:
            return "Head"
        if crawl_type == CrawlerContainer.CRAWL_TYPE_SOCIALDATA:
            return "Social data"
        if crawl_type == CrawlerContainer.CRAWL_TYPE_GET:
            return "GET"
        return ""

    def crawl(self, crawl_type, request=None) -> int | None:
        """
        Either finds crawl with parameters, or adds new crawl.
        Returns ID of request or None.
        """
        if request is None:
            WebLogger.error("Cannot crawl if request is None")
            return

        self.expire_old()
        self.trim_size()

        if self.get_size() >= self.records_size:
            self.remove_one_history()

        if self.get_size() >= self.records_size:
            return

        # Try to find existing
        found = self.find(crawl_type, request=request)
        if found is not None:
            return found

        # Create new request
        with self.lock:
            self.crawl_index += 1
            crawl_id = self.crawl_index

            item = CrawlItem(
                crawl_id=crawl_id,
                crawl_type=crawl_type,
                request=request,
            )
            self.container.append(item)

        self.expire_old()
        self.trim_size()

        return crawl_id

    def find(self, crawl_type=None, request=None) -> int | None:
        """
        Finds crawl with parameters. Returns ID or None.
        """

        for item in reversed(self.container):
            if self._match(item, crawl_type, request=request):
                return item.crawl_id
        return None

    def update(self, crawl_id=None, data=None) -> bool:
        """
        Updates results. If crawl_id cannot be found, not updated.
        Returns true if update was successful
        """
        self.expire_old()

        if data is None:
            return

        for item in reversed(self.container):
            if item.crawl_id == crawl_id:
                item.data = data
                return True
        return False

    def add(self, crawl_type=None, request=None, data=None, crawl_id=None):
        """
        Adds crawl type data for url
        """
        item_updated = False
        if crawl_id:
            crawl_item = self.get(crawl_id=crawl_id)
            if crawl_item:
                self.update(crawl_id, data)
                item_updated = True

        crawl_item = self.get(request=request)
        if crawl_item:
            self.update(crawl_item.crawl_id, data)
            item_updated = True

        if not item_updated:
            with self.lock:
                self.crawl_index += 1
                crawl_id = self.crawl_index

                crawl_item = CrawlItem(
                    crawl_id=crawl_id,
                    crawl_type=crawl_type,
                    request=request,
                    data=data,
                )

                self.container.append(crawl_item)

        self.expire_old()
        self.trim_size()

        if crawl_item:
            return crawl_item.crawl_id

    def remove(self, crawl_id):
        """
        Removes crawl at index
        @returns true if removed
        """
        found_crawl_id = False

        result = []

        for crawl_data in self.container:
            if crawl_data.crawl_id != crawl_id:
                result.append(crawl_data)
            else:
                found_crawl_id = True

        self.container = result

        return found_crawl_id

    def clear(self):
        """
        Clears entire container
        """
        self.container = []

    def get(self, crawl_id=None, crawl_type=None, request=None) -> CrawlItem | None:
        """Get crawl item by ID if not expired."""
        if not crawl_id and request:
            crawl_id = self.find(crawl_type=crawl_type, request=request)

        if crawl_id:
            for item in reversed(self.container):
                if item.crawl_id == crawl_id:
                    return item
        return None

    def leave(self, crawl_id):
        """Remove crawl explicitly."""
        result = []
        for crawl_item in self.container:
            if crawl_item.crawl_id != crawl_id:
                result.append(crawl_item)
            else:
                self.close_item(crawl_item)
        self.container = result

    def set_time_cache(self, time_cache_m):
        self.time_cache_m = time_cache_m

    def set_records_size(self, row_size):
        self.records_size = row_size

    def get_size(self):
        """Returns size of the container."""
        return len(self.container)

    # ------------------------------
    # Internal helpers
    # ------------------------------

    def expire_old(self):
        """
        Remove entries older than the time_cache window.
        Do not remove things that are in queue
        """
        cutoff = datetime.now() - timedelta(seconds=self.time_cache_m * 60)

        result = []
        for crawl_item in reversed(self.container):
            if crawl_item.timestamp > cutoff or not crawl_item.is_response():
                result.append(crawl_item)
            else:
                self.close_item(crawl_item)

        result.reverse()
        self.container = result

    def is_expired(self, crawl_item):
        return crawl_item.is_expired()

    def trim_size(self):
        """
        Enforce the records_size limit.
        Do not remove things that are in queue
        """
        if self.get_size() > self.records_size:
            result = []
            index = 0
            for crawl_item in reversed(self.container):
                if not crawl_item.is_response():
                    result.append(crawl_item)
                elif len(result) < self.records_size:
                    result.append(crawl_item)
                else:
                    self.close_item(crawl_item)
            result.reverse()
            self.container = result

    def remove_one_history(self):
        """
        Remove entries older than the time_cache window.
        Do not remove things that are in queue
        """
        one_found = False
        result = []
        for crawl_item in reversed(self.container):
            if crawl_item.is_response():
                if not one_found:
                    self.close_item(crawl_item)
                    one_found = True
                    continue
            result.append(crawl_item)
        result.reverse()
        self.container = result

    def close_item(self, crawl_item):
        # request_real does not have crawler_type nor name
        # request is JSON
        # nothing really to close, but maybe some day
        self.no_history_crawls += 1

    def get_no_crawls(self):
        return self.no_history_crawls + len(self.get_ready_items())

    def _match(self, item, crawl_type=None, request=None):
        if item is None:
            return False

        if crawl_type is not None and item.crawl_type != crawl_type:
            return False

        input_json_request = request_to_json(request)
        if request is not None and not self.match_requests(item.request, input_json_request):
            return False

        return True

    def match_requests(self, one_request,  input_request):
        if one_request and "crawler_type" in one_request:
            one_request["crawler_type"]=None
        if input_request and "crawler_type" in input_request:
            input_request["crawler_type"]=None
        if one_request and "handler_type" in one_request:
            one_request["handler_type"]=None
        if input_request and "handler_type" in input_request:
            input_request["handler_type"]=None

        if one_request and "crawler_name" not in one_request:
            one_request["crawler_name"]=None
        if input_request and "crawler_name" not in input_request:
            input_request["crawler_name"]=None
        if one_request and "handler_name" not in one_request:
            one_request["handler_name"]=None
        if input_request and "handler_name" not in input_request:
            input_request["handler_name"]=None

        if one_request["crawler_name"] != input_request["crawler_name"]:
            return False
        if one_request["handler_name"] != input_request["handler_name"]:
            return False
        if one_request["url"] != input_request["url"]:
            return False

        if one_request is None and input_request is None:
            return True

        return True

    def get_all_items(self):
        return self.container

    def get_queued_items(self):
        """
        Returns items that are not yet ready
        """
        crawl_items = []
        for crawl_item in self.container:
            if crawl_item.data is None:
                crawl_items.append(crawl_item)
        return crawl_items

    def get_ready_items(self):
        """
        Returns items that are ready
        """
        crawl_items = []
        for crawl_item in self.container:
            if crawl_item.data is not None:
                crawl_items.append(crawl_item)
        return crawl_items
