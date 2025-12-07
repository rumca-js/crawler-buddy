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
from src import CrawlerContainer
from src import CrawlerData


class CrawlerGet(object):
    def __init__(self, container, crawl_item):
        self.container = container
        self.crawl_item = crawl_item

    def run(self):
        url = self.crawl_item.url
        request = self.crawl_item.request

        try:
            webtools.WebConfig.start_display()
            all_properties = self.run_internal(url, request)
        except Exception as E:
            WebLogger.exc(
                E,
                info_text="Exception when calling getj {} {}".format(url, request),
            )
            all_properties = [{"name": "Response", "data": {
                "status_code" : HTTP_STATUS_CODE_EXCEPTION,
                "errors" :  [str(E)],
            }}]

        if webtools.SeleniumDriver.counter == 0 and webtools.WebConfig.count_chrom_processes() > 10:
            webtools.WebConfig.kill_chrom_processes()
            webtools.WebConfig.kill_xvfb_processes()

        return all_properties

    def run_internal(self, url, request=None):
        if self.crawl_item.url:
            url = self.crawl_item.url
        if self.crawl_item.request:
            if self.crawl_item.request_real.url:
                url = self.crawl_item.request_real.url
        request = self.crawl_item.request_real

        page_url = webtools.Url(url, request=request)

        all_properties = None
        try:
            print("Running:{}, with:{}".format(url, request))

            response = page_url.get_response()
            all_properties = page_url.get_all_properties(include_social=False)
        except Exception as E:
            WebLogger.exc(
                E, info_text="Exception when calling getj {}".format(url)
            )
            all_properties = [{"name": "Response", "data": {
                "status_code" : HTTP_STATUS_CODE_EXCEPTION,
                "errors" :  [str(E)],
            }}]

        self.container.update(crawl_id=self.crawl_item.crawl_id, data=all_properties)

        return all_properties


class CrawlerSocialData(object):
    def __init__(self, container, crawl_item):
        self.container = container
        self.crawl_item = crawl_item

    def run(self):
        return self.run_internal()

    def run_internal(self):
        url = self.crawl_item.url
        request = self.crawl_item.request
        if self.crawl_item.url:
            url = self.crawl_item.url
        if self.crawl_item.request:
            if self.crawl_item.request.url:
                url = self.crawl_item.request.url

        properties = None
        try:
            page_url = webtools.Url(url)
            properties = page_url.get_social_properties()
        except Exception as E:
            WebLogger.exc(
                E, info_text="Exception when calling socialj {}".format(url)
            )
            properties = [{"name": "Response", "data": {
                "status_code" : HTTP_STATUS_CODE_EXCEPTION,
                "errors" :  [str(E)],
            }}]

        self.container.update(crawl_id=self.crawl_item.crawl_id, data=properties)
        return properties


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

        row_size = self.configuration.get("history_size")

        self.container = CrawlerContainer(records_size = row_size)

        self.data = CrawlerData(self.configuration)

    def get_request_data(self, request):
        self.data.set_request(request)
        return self.data.get_request_data()

    def get_page_url(self, url, request):
        """ """

        page_url = webtools.Url(url, request=request)
        return page_url

    def get_social_properties(self, server_request, url):
        if not url:
            all_properties = [{"name": "Response", "data": {
                "status_code" : HTTP_STATUS_CODE_EXCEPTION,
                "errors" :  ["No url provided"],
            }}]
            return all_properties

        force = server_request.args.get("force")

        if not force:
            things = self.container.get(crawl_type=CrawlerContainer.CRAWL_TYPE_SOCIALDATA, url=url)
            if things:
                all_properties = things.data
                return all_properties

        crawl_id = self.container.crawl(crawl_type=CrawlerContainer.CRAWL_TYPE_SOCIALDATA, url=url)
        if crawl_id is None:
            WebLogger.error(
                info_text=f"{url} Cannot call socialj".format(url)
            )
            all_properties = [{"name": "Response", "data": {
                "status_code" : HTTP_STATUS_CODE_SERVER_TOO_MANY_REQUESTS,
                "errors" :  ["Too many crawler calls"],
            }}]

        crawl_item = self.container.get(crawl_id=crawl_id)
        crawl_runner = CrawlerSocialData(container=self.container, crawl_item=crawl_item)
        properties = crawl_runner.run()

        return properties

    def get_all_properties(self, server_request, headers=False, ping=False):
        url = server_request.args.get("url")
        force = server_request.args.get("force")

        if not url:
            all_properties = [{"name": "Response", "data": {
                "status_code" : HTTP_STATUS_CODE_EXCEPTION,
                "errors" :  ["No url provided"],
            }}]
            return all_properties

        request = self.get_request_data(server_request)

        if not request:
            all_properties = [{"name": "Response", "data": {
                "status_code" : HTTP_STATUS_CODE_EXCEPTION,
                "errors" :  ["Cannot obtain request"],
            }}]
            return all_properties

        if not force:
            things = self.container.get(crawl_type=CrawlerContainer.CRAWL_TYPE_GET, url=url, request=request)
            if things:
                all_properties = things.data

                if all_properties:
                    return all_properties

        crawl_id = self.container.crawl(crawl_type=CrawlerContainer.CRAWL_TYPE_GET, url=url, request=request)
        if crawl_id is None:
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

        crawl_item = self.container.get(crawl_id=crawl_id)
        crawl_runner = CrawlerGet(container=self.container, crawl_item = crawl_item)
        all_properties = crawl_runner.run()

        return all_properties
