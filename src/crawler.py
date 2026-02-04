"""
Main crawler
"""
import subprocess
import psutil
import json
from datetime import datetime
import time

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


def get_all_properties__too_many_requests(error_text):
    all_properties = [{"name": "Response", "data": {
        "status_code" : HTTP_STATUS_CODE_SERVER_TOO_MANY_REQUESTS,
        "errors" :  [error_text],
    }}]
    return all_properties


def get_all_properties__error(E, error_text):
    all_properties = [{"name": "Response", "data": {
        "status_code" : HTTP_STATUS_CODE_SERVER_TOO_MANY_REQUESTS,
        "errors" :  [str(E) + " " + error_text],
    }}]
    return all_properties


class CrawlerTypeGet(object):
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
            all_properties = get_all_properties__error(E, "Cannot obtain GET information")

        if webtools.SeleniumDriver.counter == 0 and webtools.WebConfig.count_chrom_processes() > 10:
            webtools.WebConfig.kill_chrom_processes()
            webtools.WebConfig.kill_xvfb_processes()

        return all_properties

    def run_internal(self, url, request=None):
        url = self.crawl_item.get_url()
        request = self.crawl_item.request_real

        page_url = webtools.Url(url=url, request=request)

        all_properties = None
        try:
            print("Running:{}, with:{}".format(url, request))

            response = page_url.get_response()
            all_properties = page_url.get_all_properties(include_social=False)
        except Exception as E:
            WebLogger.exc(
                E, info_text="Exception when calling getj {}".format(url)
            )
            all_properties = get_all_properties__error(E, "Cannot obtain GET information")

        self.container.update(crawl_id=self.crawl_item.crawl_id, data=all_properties)

        return all_properties


class CrawlerTypeSocialData(object):
    def __init__(self, container, crawl_item):
        self.container = container
        self.crawl_item = crawl_item

    def run(self):
        return self.run_internal()

    def run_internal(self):
        url = self.crawl_item.get_url()
        request = self.crawl_item.request

        all_properties = None
        try:
            page_url = webtools.Url(url)
            all_properties = page_url.get_social_properties()

            # TODO how to handle it?

            if all_properties is None:
                all_properties = get_all_properties__too_many_requests("Cannot obtain social data")
        except Exception as E:
            WebLogger.exc(
                E, info_text="Exception when calling socialj {}".format(url)
            )
            all_properties = [{"name": "Response", "data": {
                "status_code" : HTTP_STATUS_CODE_EXCEPTION,
                "errors" :  [str(E)],
            }}]
            all_properties = get_all_properties__error(E, "Cannot obtain social data")

        self.container.update(crawl_id=self.crawl_item.crawl_id, data=all_properties)
        return all_properties


def crawler_builder(container, crawl_item):
    if crawl_item.crawl_type == CrawlerContainer.CRAWL_TYPE_GET:
        crawl = CrawlerTypeGet(container=container, crawl_item = crawl_item)
    elif crawl_item.crawl_type == CrawlerContainer.CRAWL_TYPE_SOCIALDATA:
        crawl = CrawlerTypeSocialData(container=container, crawl_item=crawl_item)
    return crawl


class Crawler(object):
    """
    Crawler
    """
    def __init__(self):
        """ Constructor """
        self.configuration = Configuration()
        self.multi_process = False

        """
        We cannot allow to run 100x of yt-dlp. We need to keep it real.
        Configurable because people might want more.
        """

        row_size = self.configuration.get("max_history_records")

        self.container = CrawlerContainer(records_size = row_size)

        self.data = CrawlerData(self.configuration)

    def get_request_data(self, request):
        self.data.set_request(request)
        return self.data.get_request_data()

    def get_page_url(self, url, request):
        """ """

        page_url = webtools.Url(url, request=request)
        return page_url

    def get_crawl_with_method(self, crawl_type, url=None, request=None, force=False):
        if not url:
            if self.request:
                url = self.request.url

        if not url:
            all_properties = [{"name": "Response", "data": {
                "status_code" : HTTP_STATUS_CODE_EXCEPTION,
                "errors" :  ["No url provided"],
            }}]
            return all_properties

        if not force:
            things = self.container.get(crawl_type=crawl_type, url=url, request=request)
            if things:
                if things.data is None:
                    data = self.wait_for_response(crawl_id)
                    if data:
                        return data
                    return get_all_properties__too_many_requests("Not yet ready")

                return things.data

        crawl_id = self.container.crawl(crawl_type=crawl_type, url=url, request=request)
        if crawl_id is None:
            WebLogger.error(
                info_text=f"{url} Cannot crawl".format(url)
            )
            all_properties = get_all_properties__too_many_requests("Crawl method")
            return all_properties

        if self.multi_process:
            data = self.wait_for_response(crawl_id)
            if data:
                return data
            all_properties = get_all_properties__too_many_requests("Crawl method - data not ready")
        else:
            crawl_item = self.container.get(crawl_id)
            crawl = crawler_builder(self.container, crawl_item)
            data = crawl.run()
            if data:
                return data
            all_properties = get_all_properties__too_many_requests("Crawl method - data not ready")
        return all_properties

    def get_social_properties(self, server_request, url):
        url = server_request.args.get("url")
        force = server_request.args.get("force")

        result = self.get_crawl_with_method(url=url, crawl_type=CrawlerContainer.CRAWL_TYPE_SOCIALDATA, force=force)

        return result

    def get_all_properties(self, server_request, headers=False, ping=False):
        url = server_request.args.get("url")
        force = server_request.args.get("force")

        request = self.get_request_data(server_request)

        result = self.get_crawl_with_method(request=request, url=url, crawl_type=CrawlerContainer.CRAWL_TYPE_GET, force=force)
        return result

    def wait_for_response(self, crawl_id):
        """
        Waits for the response
        The client can disconnect if he wants ib
        """

        """
        start_time = time.time()
        crawl_item = self.container.get(crawl_id=crawl_id)

        time_wait_s = 100
        if crawl_item.request_real:
            request_time_s = 0
            if crawl_item.request_real.timeout_s:
                request_time_s += crawl_item.request_real.timeout_s
            if crawl_item.request_real.delay_s:
                request_time_s += crawl_item.request_real.delay_s

            if request_time_s > 0:
                time_wait_s = request_time_s

        while(time.time() - start_time < time_wait_s):
            crawl_item = self.container.get(crawl_id=crawl_id)
            if crawl_item.data is not None:
                return crawl_item.data
            time.sleep(0.1)
        """

        while True:
            crawl_item = self.container.get(crawl_id=crawl_id)
            if crawl_item.data is not None:
                return crawl_item.data
            time.sleep(0.1)

    def set_multi_process(self):
        self.multi_process = True
