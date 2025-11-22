"""
Main crawler
"""
import subprocess
import psutil
import json
from datetime import datetime

from webtoolkit import (
  WebLogger,
  RemoteServer,
  HTTP_STATUS_CODE_EXCEPTION,
  HTTP_STATUS_CODE_SERVER_TOO_MANY_REQUESTS,
)

from src import webtools
from src.configuration import Configuration
from src import CrawlerHistory
from src import CrawlerQueue
from src import CrawlerData


class Crawler(object):
    """
    Crawler
    """
    def __init__(self):
        """ Constructor """
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

    def get_social_properties(self, request, url):
        force = request.args.get("force")

        if not force:
            things = self.social_history.find(url=url)
            if things:
                index, timestamp, all_properties = things

                return all_properties

        crawler_index = self.social_queue.enter(url)
        if crawler_index is None:
            WebLogger.error(
                info_text=f"{url} Cannot call socialj".format(url)
            )
            return None

        properties = None
        try:
            page_url = webtools.Url(url)
            properties = page_url.get_social_properties()
        except Exception as E:
            WebLogger.exc(
                E, info_text="Exception when calling socialj {}".format(url)
            )
            properties = None

        self.social_queue.leave(crawler_index)
        self.social_history.add((url, properties))

        return properties

    def get_page_url(self, url, request):
        """ """

        page_url = webtools.Url(url, request=request)
        return page_url

    def get_all_properties(self, request, headers=False, ping=False):
        url = request.args.get("url")
        force = request.args.get("force")

        if not url:
            all_properties = [{"name": "Response", "data": {
                "status_code" : webtools.HTTP_STATUS_CODE_EXCEPTION,
                "errors" :  ["No url provided"],
            }}]
            return all_properties

        request = self.get_request_data(request)

        if not request:
            all_properties = [{"name": "Response", "data": {
                "status_code" : HTTP_STATUS_CODE_EXCEPTION,
                "errors" :  ["Cannot obtain request"],
            }}]
            return all_properties

        name = request.crawler_name

        if not force:
            things = self.get_history().find(url=url, crawler_name=name)

            if things:
                print("Returning from saved properties")
                index, timestamp, all_properties = things

                if all_properties:
                    return all_properties

        # TODO what if there is exception
        crawl_index = self.queue.enter(url, request)
        if crawl_index is None:
            WebLogger.error("Too many crawler calls".format(url, request))
            all_properties = [{"name": "Response", "data": {
                "status_code" : HTTP_STATUS_CODE_SERVER_TOO_MANY_REQUESTS,
                "errors" :  ["Too many crawler calls"],
            }}]
            return all_properties

        if headers:
            request.request_type = "head"
        elif ping:
            request.request_type = "ping"

        try:
            webtools.WebConfig.start_display()
            all_properties = self.run(url, request)
        except Exception as E:
            WebLogger.exc(
                E,
                info_text="Exception when calling getj {} {}".format(url, request),
            )
            all_properties = None

        self.queue.leave(crawl_index)
        self.url_history.add((url, all_properties))

        if webtools.SeleniumDriver.counter == 0 and webtools.WebConfig.count_chrom_processes() > 10:
            webtools.WebConfig.kill_chrom_processes()
            webtools.WebConfig.kill_xvfb_processes()

        if not all_properties:
            all_properties = [{"name": "Response", "data": {
                "status_code" : HTTP_STATUS_CODE_EXCEPTION,
                "errors" :  ["No properties found"],
            }}]

        response = RemoteServer.read_properties_section("Response", all_properties)
        # WebLogger.debug(info_text = "Crawling response: ", detail_text = str(response))

        return all_properties

    def run(self, url, request=None):
        if not request:
            WebLogger.error(
                "Url:{} Cannot run request without request".format(url)
            )
            return

        page_url = self.get_page_url(url, request)

        if not page_url:
            WebLogger.error(
                "Could not create page url for {} {}".format(url, request)
            )
            return

        try:
            print("Running:{}, with:{}".format(url, request))

            response = page_url.get_response()
            all_properties = page_url.get_all_properties(include_social=False)
        except Exception as e:
            raise

        return all_properties

