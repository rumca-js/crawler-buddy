import time
from datetime import datetime
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

from webtoolkit import UrlLocation
from webtoolkit import WebLogger

from .crawler import crawler_builder
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
        self.lock = threading.Lock()           # protects running_ids
        self.container_lock = threading.Lock() # protects container

        self.poll_interval = poll_interval
        self.shutdown_flag = False
        self.verbose = verbose

    def run_item(self, item):
        """Actual crawl logic here."""
        if self.verbose:
            print(f"[RUN]  {item.url}")

        try:
            crawl = crawler_builder(container=self.container, crawl_item=item)

            if crawl:
                crawl.run()
        except Exception as E:
            WebLogger.exc(E, "Error in task runner")

        if self.verbose:
            print(f"[DONE] {item.url}")

        return item.crawl_id

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
        return len(self.running_ids) == 0

    def _on_done(self, future):
        """Cleanup when tasks finish."""

        crawl_id = None
        try:
            crawl_id = future.result()
        except Exception as E:
            print("Error in worker:", E)
            return

        if crawl_id:
            with self.lock:
                self.running_ids.discard(crawl_id)

    def start(self):
        """
        Runs forever until stop() is called.
        Continuously checks container for new items.
        """

        print("[TaskRunner] Started (indefinite mode)")

        try:
            while not self.shutdown_flag:
                submitted_any = False

                with self.container_lock:
                    for item in list(self.container.get_queued_items()):
                        if item.data is None:
                            if item.crawl_id and self.attempt_submit(item):
                                submitted_any = True

                # Sleep a bit if no new work appeared
                if not submitted_any:
                    time.sleep(self.poll_interval)
        except Exception as E:
            print("Exception in TaskRunner: " + str(E))

        print("[TaskRunner] Stopping… waiting for tasks to finish.")
        self.executor.shutdown(wait=True)
        print("[TaskRunner] Stopped.")

    def stop(self):
        """Graceful stop signal."""
        self.shutdown_flag = True


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
