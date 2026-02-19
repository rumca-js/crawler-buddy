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

from .crawler import crawler_builder, get_all_properties__error
from .crawlercontainer import CrawlerContainer


class TaskRunner(object):

    def __init__(self, container, max_workers=5, poll_interval=0.1, verbose=True):
        """
        container: shared list of CrawlItem (updated externally)
        poll_interval: how often to poll container for new items (seconds)
        """
        self.container = container

        if max_workers is None:
            max_workers = 5
        self.executor = ThreadPoolExecutor(max_workers=max_workers)

        self.running_ids = set()
        self.futures = []
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
        return len(self.futures)

    def run_item(self, item):
        """Actual crawl logic here."""
        try:
            if self.verbose:
                print(f"[RUN]  {item.url}")

            crawl = crawler_builder(container=self.container, crawl_item=item)

            if crawl:
                crawl.run()

            if self.verbose:
                print(f"[DONE] {item.url}")

            return item.crawl_id
        except Exception as E:
            WebLogger.exc(E, "Error in task runner")

    def attempt_submit(self, item):
        """
        Attempts to submit a task if URL is not running already.
        Returns True if submitted.
        """
        with self.lock:
            if not self.is_item_crawl_ok(item):
                return False

            self.running_ids.add(item.crawl_id)
            future = self.executor.submit(self.run_item, item)
            future.add_done_callback(self._on_done)
            self.futures.append(future)
        return True

    def is_running(self, crawl_id):
        return crawl_id in self.running_ids

    def is_item_crawl_ok(self, item):
        """
        If new thing to run has the same domain as the running one,
        then do not add
        """
        if item.crawl_id in self.running_ids:
            return False

        selenium_limit = True

        running_urls = set()
        queued_items = self.container.get_queued_items()
        for queued_item in queued_items:
            if queued_item.crawl_id in self.running_ids:
                running_urls.add(queued_item.get_url())

                if selenium_limit:
                    if self.is_selenium_both(item, queued_item):
                        return False

        running_domains = set()
        for queued_url in running_urls:
            location = UrlLocation(queued_url)
            running_domains.add(location.get_domain_only(no_www=True))

        location = UrlLocation(item.get_url())
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
        return len(self.futures) == 0

    def _on_done(self, future):
        """Cleanup when tasks finish."""

        crawl_id = None
        try:
            crawl_id = future.result()
        except Exception as E:
            WebLogger.exc(E, "Error in worker:")

        with self.lock:
            if future in self.futures:
                self.futures.remove(future)

            if crawl_id is not None:
                self.running_ids.discard(crawl_id)
            else:
                WebLogger.error("I do not know which crawl_id to remove")

    def start(self):
        """
        Runs forever until stop() is called.
        Continuously checks container for new items.
        """

        print("[TaskRunner] Started (indefinite mode)")

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

        except Exception as E:
            WebLogger.exc(E, "Exception in TaskRunner")

        print("[TaskRunner] Stopping… waiting for tasks to finish.")
        self.executor.shutdown(wait=True)
        print("[TaskRunner] Stopped.")

    def fix_leftovers(self):
        if len(self.running_ids) > 0:
            running_copy = copy.copy(self.running_ids)
            for running_id in running_copy:
                running_item = self.container.get(crawl_id = running_id)
                if running_item:
                    # if has already response - remove it from running
                    if running_item.is_response():
                        with self.lock:
                            self.running_ids.discard(running_id)
                        WebLogger.error(f"Cleaning up running ids {running_id}")
                if not running_item:
                    # if not in queue, then something is wrong
                    with self.lock:
                        self.running_ids.discard(running_id)
                    WebLogger.error(f"Cleaning up running ids {running_id}")

        with self.lock:
            self.futures = [f for f in self.futures if not f.done()]
            if len(self.futures) == 0 and len(self.running_ids) > 0:
                WebLogger.error("Cleaned up Running IDS")
                self.running_ids = []

    def is_thread_ok(self):
        if self.health_date:
            return datetime.now() - self.health_date < timedelta(minutes=5)
        return False

    def stop(self):
        """Graceful stop signal."""
        self.shutdown_flag = True

    def close(self):
        self.executor.shutdown(wait=True, cancel_futures=True)


def start_runner_thread(container, max_workers=5):
    """
    Creates and starts a daemon thread that runs a Runner instance.
    Returns the thread object.
    """

    runner = TaskRunner(container, max_workers=max_workers)

    thread = threading.Thread(
        target=runner.start,
        args=(),          # start() gets container through instance
        daemon=True       # daemon thread
    )

    thread.start()
    return thread, runner
