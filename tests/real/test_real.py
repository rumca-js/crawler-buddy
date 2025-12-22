"""
With this script you can compare solutions.

This should be treated with a grain of salt, since all of them are called through OS subprocess.
To make crawlers results more objective all are called that way

In my setup it was around:
 requests: 2.9 [s]
 beautiful soup: 4.1 [s]
 playwright: 10.42 [s]
 selenium: not installed / missing
 selenium undetected: 12.62 [s]

# TODO check if status code is valid for all
"""

import time
import subprocess
import unittest
import importlib
from pathlib import Path

from webtoolkit import file_to_response
import webtoolkit
import src.webtools.crawlers
from src.webtools import Url
from src.webtools.webconfig import WebConfig


# change test webpage to see if other pages can be scraped using different scrapers
test_webpage = "https://google.com"


class TestUrl(unittest.TestCase):
    def call_process(self, input_script, url = None):
        start_time = time.time()

        print(f"Running script {input_script} {url}")

        path = Path("out.txt")
        if path.exists():
            path.unlink()

        if url == None:
            url = test_webpage

        timeout_s = 55

        subprocess.check_call(
            "poetry run python {} --url {} --output-file {} --timeout {}".format(
                input_script, url, "out.txt", timeout_s
            ),
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=timeout_s,
        )

        response = file_to_response("out.txt")

        execution_time = time.time() - start_time
        print(f"Time: {execution_time}")

        if not response:
            print("No respone")
        if response and response.is_invalid():
            print("Response is invalid")

        return [input_script + " " + url, execution_time, response]

    def call_crawler(self, test_link, name):
        print(f"Running {test_link} with {name} crawler")

        start_time = time.time()
        execution_time = None
        response = None

        crawler_class = WebConfig.get_crawler_from_string(name)
        crawler = crawler_class(url=test_link)
        if not crawler.is_valid():
            print(f"Crawler is {name} disabled")
        else:
            response = crawler.run()
            crawler.close()

            execution_time = time.time() - start_time
            print(f"Time: {execution_time}")

            if not response:
                print("No respone")
            if response and response.is_invalid():
                print("Response is invalid")
            if response and response.is_valid():
                print("Response is valid")

        return [name, execution_time, response]

    def call_url(self, url):
        start_time = time.time()

        print(f"Url test: {url}")
        url = Url(url = url)

        handler = url.get_handler()
        response = url.get_response()

        if not response:
            print("No respone")
        if response and response.is_invalid():
            print("Response is invalid")

        if url.get_title() is None:
            print("Title is None!")

        feeds = url.get_feeds()
        if feeds:
            print("Feeds {}".format(len(feeds)))

        streams = url.get_streams()
        if streams:
            print("Streams {}".format(len(streams)))

        entries = url.get_entries()
        if entries:
            print("Entries {}".format(len(entries)))

        execution_time = time.time() - start_time
        print(f"Time: {execution_time}")

        properties = url.get_social_properties()
        print(properties)

        return handler, response

    def test_crawlers(self):
        _, _, response = self.call_crawler(test_webpage, "RequestsCrawler")
        _, _, response = self.call_crawler(test_webpage, "CurlCffiCrawler")
        _, _, response = self.call_crawler("https://www.youtube.com/@LinusTechTips", "CurlCffiCrawler")
        _, _, response = self.call_crawler(test_webpage, "HttpxCrawler")
        _, _, response = self.call_crawler(test_webpage, "HttpMorphCrawler")
        _, _, response = self.call_crawler(test_webpage, "StealthRequestsCrawler")
        _, _, response = self.call_crawler(test_webpage, "SeleniumChromeHeadless")
        _, _, response = self.call_crawler(test_webpage, "SeleniumChromeFull")
        _, _, response = self.call_crawler(test_webpage, "SeleniumUndetected")
        _, _, response = self.call_crawler(test_webpage, "SeleniumWireFull")

        _, _, response = self.call_process("crawleebeautifulsoup.py")
        # _, _, response = self.call_crawleeplaywright()

    def test_crawl_script(self):
        print("-----------")
        print("Testing how scripts exchange request/response data")
        print("-----------")
        _, _, response = self.call_process("crawl.py", "https://www.youtube.com/watch?v=9yanqmc01ck")
        _, _, response = self.call_process("crawl.py", "https://www.youtube.com/feeds/videos.xml?channel_id=UCXuqSBlHAE6Xw-yeJA0Tunw")
        _, _, response = self.call_process("crawl.py", "https://www.youtube.com/channel/UCXuqSBlHAE6Xw-yeJA0Tunw")
        _, _, response = self.call_process("crawl.py", "https://www.youtube.com/@LinusTechTips")

    def test_google(self):
        handler, response = self.call_url(url = "https://www.google.com")

        self.assertEqual(handler.__class__.__name__, "HttpPageHandler")

        self.assertTrue(handler.get_title())
        self.assertTrue(len(handler.get_streams()) == 1)
        self.assertTrue(len(handler.get_feeds()) == 0)
        self.assertTrue(len(handler.get_entries()) == 0)

        self.assertTrue(response.is_valid())

    def test_youtube_video(self):
        handler, response = self.call_url(url = "https://www.youtube.com/watch?v=9yanqmc01ck")

        self.assertEqual(handler.__class__.__name__, "YouTubeVideoHandlerJson")

        self.assertTrue(handler.get_title())
        self.assertEqual(len(handler.get_streams()), 2)
        self.assertEqual(len(handler.get_feeds()), 1)
        self.assertTrue(len(handler.get_entries()) == 0)

        self.assertTrue(response.is_valid())

    def test_youtube_channel__feed(self):
        handler, response = self.call_url(url = "https://www.youtube.com/feeds/videos.xml?channel_id=UCXuqSBlHAE6Xw-yeJA0Tunw")

        self.assertEqual(handler.__class__.__name__, "YouTubeChannelHandlerJson")

        self.assertTrue(handler.get_title())
        self.assertTrue(len(handler.get_streams()) == 2)
        self.assertTrue(len(handler.get_feeds()) == 1)
        self.assertTrue(len(handler.get_entries()) > 0)

        self.assertTrue(response.is_valid())

    def test_youtube_channel__id(self):
        handler, response = self.call_url(url = "https://www.youtube.com/channel/UCXuqSBlHAE6Xw-yeJA0Tunw")

        self.assertEqual(handler.__class__.__name__, "YouTubeChannelHandlerJson")

        self.assertTrue(handler.get_title())
        self.assertTrue(len(handler.get_streams()) == 2)
        self.assertTrue(len(handler.get_feeds()) == 1)
        self.assertTrue(len(handler.get_entries()) > 0)

        self.assertTrue(response.is_valid())

    def test_youtube_channel__name(self):
        handler, response = self.call_url(url = "https://www.youtube.com/@LinusTechTips")

        self.assertEqual(handler.__class__.__name__, "YouTubeChannelHandlerJson")

        self.assertTrue(handler.get_title())
        self.assertEqual(handler.get_title(), "Linus Tech Tips")
        self.assertTrue(len(handler.get_streams()) == 1)
        self.assertEqual(len(handler.get_feeds()), 1)
        self.assertTrue(len(handler.get_entries()) == 0)

        self.assertTrue(response.is_valid())

    def test_github(self):
        handler, response = self.call_url(url = "https://www.github.com/rumca-js/Internet-Places-Database")

        self.assertEqual(handler.__class__.__name__, "GitHubUrlHandler")

        self.assertTrue(handler.get_title())
        self.assertTrue(len(handler.get_streams()) == 1)
        self.assertTrue(len(handler.get_feeds()) == 2)
        self.assertTrue(len(handler.get_entries()) == 0)

        self.assertTrue(response.is_valid())

    def test_reddit__channel(self):
        handler, response = self.call_url(url = "https://www.reddit.com/r/wizardposting")

        self.assertEqual(handler.__class__.__name__, "RedditUrlHandler")

        self.assertTrue(handler.get_title())
        self.assertTrue(len(handler.get_streams()) == 2)
        self.assertTrue(len(handler.get_feeds()) == 1)
        self.assertTrue(len(handler.get_entries()) == 0)

        self.assertTrue(response.is_valid())

    def test_reddit__post(self):
        handler, response = self.call_url(url = "https://www.reddit.com/r/wizardposting/comments/1olomjs/screw_human_skeletons_im_gonna_get_more_creative/")

        self.assertEqual(handler.__class__.__name__, "RedditUrlHandler")

        self.assertTrue(handler.get_title())
        self.assertTrue(len(handler.get_streams()) == 2)
        self.assertTrue(len(handler.get_feeds()) == 1)
        self.assertTrue(len(handler.get_entries()) == 0)

        self.assertTrue(response.is_valid())

        #import httpmorph
        #response =  httpmorph.get("https://www.youtube.com/channel/UCXuqSBlHAE6Xw-yeJA0Tunw", timeout=30)
        #print(reponse.status_code)
