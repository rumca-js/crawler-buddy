import time
import copy
from datetime import datetime, timedelta
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

from webtoolkit import (
  UrlLocation,
  WebLogger,
  HTTP_STATUS_CODE_EXCEPTION,
)
from utils.systemmonitoring import get_memory_info

from .crawler import crawler_builder, get_all_properties__error
from .crawlercontainer import CrawlerContainer


class TaskRunner(object):

    def __init__(self, container, max_workers=5, poll_interval=0.1, no_executor=False, verbose=True):
        """
        container: shared list of CrawlItem (updated externally)
        poll_interval: how often to poll container for new items (seconds)
        """
        self.container = container
        self.no_executor = no_executor

        if max_workers is None:
            max_workers = 5
        self.executor = ThreadPoolExecutor(max_workers=max_workers)

        self.running_ids = {}
        self.lock = threading.Lock()           # protects running_ids
        self.container_lock = threading.Lock() # protects container

        self.poll_interval = poll_interval
        self.shutdown_flag = False
        self.verbose = verbose
        self.health_date = None

        self.set_thread_ok()

    def set_thread_ok(self):
        self.health_date = datetime.now()

    def get_size(self):
        return len(self.running_ids)

    def run_item(self, item):
        """Actual crawl logic here."""
        try:
            if self.verbose:
                WebLogger.debug(f"[RUN]  {item.url}")

            crawl = crawler_builder(container=self.container, crawl_item=item)

            if crawl:
                crawl.run()

            if self.verbose:
                WebLogger.debug(f"[DONE] {item.url}")

            return item.crawl_id
        except Exception as E:
            WebLogger.exc(E, "Error in task runner")
            try:
                return item.crawl_id
            except Exception as E:
                WebLogger.exc(E, "Error in task runner2")

    def attempt_submit(self, crawl_item):
        """
        Attempts to submit a task if URL is not running already.
        Returns True if submitted.
        """
        if not self.is_item_crawl_ok(crawl_item):
            return False

        if self.no_executor:
            self.run_item(crawl_item)
        else:
            with self.lock:
                future = self.executor.submit(self.run_item, crawl_item)
                future.add_done_callback(self._on_done)
                self.running_ids[crawl_item.crawl_id] = future
        return True

    def is_running(self, crawl_id):
        return crawl_id in self.running_ids

    def is_item_crawl_ok(self, crawl_item):
        """
        If new thing to run has the same domain as the running one,
        then do not add
        """
        if crawl_item.crawl_id in self.running_ids:
            return False

        selenium_limit = True

        running_urls = set()
        queued_items = self.container.get_queued_items()
        for queued_item in queued_items:
            if queued_item.crawl_id in self.running_ids:
                running_urls.add(queued_item.get_url())

                if selenium_limit:
                    if self.is_selenium_both(crawl_item, queued_item):
                        return False

        running_domains = set()
        for queued_url in running_urls:
            location = UrlLocation(queued_url)
            running_domains.add(location.get_domain_only(no_www=True))

        location = UrlLocation(crawl_item.get_url())
        this_domain = location.get_domain_only(no_www=True)

        if this_domain and this_domain in running_domains:
            return False

        return True

    def is_selenium_both(self, one, two):
        if one.request_real and one.request_real.crawler_name and one.request_real.crawler_name.find("Selenium"):
              if two.request_real and two.request_real.crawler_name and two.request_real.crawler_name.find("Selenium") >= 0:
                  return True

        return False

    def is_empty(self):
        return len(self.running_ids) == 0

    def _on_done(self, future):
        """Cleanup when tasks finish."""

        crawl_id = None
        try:
            crawl_id = future.result()

            if crawl_id is None:
                for runnning_crawl_id, running_future in self.running_ids.items():
                    if future == running_future:
                        crawl_id = runnning_crawl_id

        except Exception as E:
            WebLogger.exc(E, "Error in worker:")

        with self.lock:
            if crawl_id in self.running_ids:
                del self.running_ids[crawl_id]

    def dispose(self, crawl_id):
        if crawl_id in self.running_ids:
            del self.running_ids[crawl_id]
        else:
            WebLogger.error(f"Cannot remove crawl id {crawl_id}")

    def start(self):
        """
        Runs forever until stop() is called.
        Continuously checks container for new items.
        """

        WebLogger.debug("[TaskRunner] Started (indefinite mode)")

        try:
            while not self.shutdown_flag:
                self.set_thread_ok()

                submitted_any = False

                with self.container_lock:
                    for item in list(self.container.get_queued_items()):
                        if item.data is None:
                            if item.crawl_id and self.attempt_submit(item):
                                submitted_any = True

                    self.fix_leftovers()

                # Sleep a bit if no new work appeared
                if not submitted_any:
                    time.sleep(self.poll_interval)

                memory_info = get_memory_info()
                if memory_info["memory_percentage"] > 95.0:
                    WebLogger.error("[TaskRunner] Stopping… virtual memory eaten.")
                    break

        except Exception as E:
            WebLogger.exc(E, "Exception in TaskRunner")

        WebLogger.debug("[TaskRunner] Stopping… waiting for tasks to finish.")
        self.executor.shutdown(wait=True)
        WebLogger.debug("[TaskRunner] Stopped.")

    def fix_leftovers(self):
        result = []
        to_delete = []
        for crawl_id, future in self.running_ids.items():
            if future.done():
                to_delete.append(crawl_id)

        with self.lock:
            for crawl_id in to_delete:
                del self.running_ids[crawl_id]

    def is_thread_ok(self):
        if self.health_date:
            return datetime.now() - self.health_date < timedelta(minutes=5)
        return False

    def stop(self):
        """Graceful stop signal."""
        self.shutdown_flag = True

    def close(self):
        self.executor.shutdown(wait=True, cancel_futures=True)


def start_runner_thread(container, max_workers=5, no_executor=False):
    """
    Creates and starts a daemon thread that runs a Runner instance.
    Returns the thread object.
    """

    runner = TaskRunner(container, max_workers=max_workers, no_executor=no_executor)

    thread = threading.Thread(
        target=runner.start,
        args=(),          # start() gets container through instance
        daemon=True       # daemon thread
    )

    thread.start()
    return thread, runner
