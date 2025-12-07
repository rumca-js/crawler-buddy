from .crawler import CrawlerGet, CrawlerSocialData
from .crawlercontainer import CrawlerContainer
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import threading
import time


class TaskRunner(object):

    def __init__(self, container, max_workers=5, poll_interval=0.1):
        """
        container: shared list of CrawlItem (updated externally)
        poll_interval: how often to poll container for new items (seconds)
        """
        self.container = container
        self.executor = ThreadPoolExecutor(max_workers=max_workers)

        self.running_urls = set()
        self.lock = threading.Lock()           # protects running_urls
        self.container_lock = threading.Lock() # protects container

        self.poll_interval = poll_interval
        self.shutdown_flag = False

    def run_item(self, item):
        """Actual crawl logic here."""
        print(f"[RUN]  {item.url}")
        if item.crawl_type == CrawlerContainer.CRAWL_TYPE_GET:
            crawl = CrawlerGet(container=self.container, crawl_item = item)
            crawl.run()
        elif item.crawl_type == CrawlerContainer.CRAWL_TYPE_SOCIAL:
            crawl = CrawlerSocialData(container=self.container, crawl_item=item)
            crawl.run()
        else:
            raise NotImplemented("Not implemented")

        # self.container.leave(item.crawl_id)
        print(f"[DONE] {item.url}")
        return item.crawl_id

    def attempt_submit(self, item):
        """
        Attempts to submit a task if URL is not running already.
        Returns True if submitted.
        """
        with self.lock:
            if item.crawl_id in self.running_urls:
                return False
            self.running_urls.add(item.crawl_id)

        future = self.executor.submit(self.run_item, item)
        future.add_done_callback(self._on_done)
        return True

    def is_empty(self):
        return len(self.running_urls) == 0

    def _on_done(self, future):
        """Cleanup when tasks finish."""
        try:
            crawl_id = future.result()
        except Exception as e:
            print("Error in worker:", e)
            return

        with self.lock:
            self.running_urls.discard(crawl_id)

    def start(self):
        """
        Runs forever until stop() is called.
        Continuously checks container for new items.
        """

        print("[Runner] Started (indefinite mode)")

        while not self.shutdown_flag:
            submitted_any = False

            with self.container_lock:
                for item in list(self.container.container):
                    if item.data is None:
                        if item.crawl_id and self.attempt_submit(item):
                            submitted_any = True

            # Sleep a bit if no new work appeared
            if not submitted_any:
                time.sleep(self.poll_interval)

        print("[Runner] Stopping… waiting for tasks to finish.")
        self.executor.shutdown(wait=True)
        print("[Runner] Stopped.")

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
