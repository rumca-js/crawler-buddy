import subprocess
import psutil
import json
from datetime import datetime
from collections import OrderedDict
from src import webtools
from src.configuration import Configuration
from src import CrawlerHistory
from src import CrawlerQueue
from src import CrawlerData


class Crawler(object):
    def __init__(self):
        self.configuration = Configuration()

        """
        We cannot allow to run 100x of yt-dlp. We need to keep it real.
        Configurable because people might want more.
        """

        self.queue = CrawlerQueue(self.configuration.get("max_queue_size"))
        self.url_history = CrawlerHistory(self.configuration.get("history_size"))

        self.social_queue = CrawlerQueue(self.configuration.get("max_queue_size"))
        self.social_history = CrawlerHistory(self.configuration.get("history_size"))

        self.data = CrawlerData(self.configuration)

    def get_history(self):
        return self.url_history

    def get_request_data(self, request):
        self.data.set_request(request)
        return self.data.get_request_data()

    def get_social_properties(self, url):
        things = self.social_history.find(url=url)
        if things:
            index, timestamp, all_properties = things

            return all_properties

        crawler_index = self.social_queue.enter(url)
        if crawler_index is None:
            webtools.WebLogger.exc(
                E, info_text="Exception when calling socialj {}".format(url)
            )
            return None

        properties = None
        try:
            page_url = webtools.Url(url)
            properties = page_url.get_social_properties()
        except Exception as E:
            webtools.WebLogger.exc(
                E, info_text="Exception when calling socialj {}".format(url)
            )
            properties = None

        self.social_queue.leave(crawler_index)
        self.social_history.add((url, properties))

        return properties

    def get_page_url(self, url, crawler_data):
        """ """

        page_url = webtools.Url(url, settings=crawler_data)
        return page_url

    def get_all_properties(self, request, headers=False, ping=False):
        url = request.args.get("url")

        if not url:
            return {"success": False, "error": "No url provided"}

        self.data.set_request(request)
        crawler_data = self.data.get_request_data()

        if not crawler_data:
            return {"success": False, "error": "Cannot obtain crawler data"}

        name = None
        if "name" in crawler_data:
            name = crawler_data["name"]
        crawler = None
        if "crawler" in crawler_data:
            crawler = crawler_data["crawler"].__class__.__name__

        things = self.get_history().find(url=url, crawler_name=name, crawler=crawler)

        if things:
            print("Returning from saved properties")
            index, timestamp, all_properties = things

            if all_properties:
                return all_properties

        # TODO what if there is exception
        crawl_index = self.queue.enter(url, crawler_data)
        if crawl_index is None:
            webtools.WebLogger.error("Too many crawler calls".format(url, crawler_data))
            return

        crawler_data["settings"]["headers"] = headers
        crawler_data["settings"]["ping"] = ping

        try:
            webtools.WebConfig.start_display()
            all_properties = self.run(url, crawler_data)
        except Exception as E:
            webtools.WebLogger.exc(
                E,
                info_text="Exception when calling getj {} {}".format(url, crawler_data),
            )
            all_properties = None

        self.queue.leave(crawl_index)
        self.url_history.add((url, all_properties))

        if not all_properties:
            return {"success": False, "error": "No properties found"}

        return all_properties

    def run(self, url, crawler_data=None):
        if not crawler_data:
            webtools.WebLogger.error(
                "Url:{} Cannot run request without crawler_data".format(url)
            )
            return

        page_url = self.get_page_url(url, crawler_data)

        if not page_url:
            webtools.WebLogger.error(
                "Could not create page url for {} {}".format(url, crawler_data)
            )
            return

        try:
            print("Running:{}, with:{}".format(url, crawler_data))

            response = page_url.get_response()
            all_properties = page_url.get_properties(full=True, include_social=False)
        except Exception as e:
            raise

        if webtools.WebConfig.count_chrom_processes() > 30:
            webtools.WebLogger.error("Too many chrome processes")
            webtools.WebConfig.kill_chrom_processes()

        return all_properties

