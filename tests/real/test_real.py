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

        return [input_script + " " + url, execution_time, response]

    def call_crawler(self, test_link, name):
        print(f"Running {test_link} with {name} crawler")

        start_time = time.time()
        execution_time = None
        response = None

        crawler_class = WebConfig.get_crawler_from_string(name)
        crawler = crawler_class(url=test_link)
        if crawler.is_valid():
            response = crawler.run()
            crawler.close()

            execution_time = time.time() - start_time

        return [name, execution_time, response]

    def call_url(self, url):
        start_time = time.time()

        print(f"Url test: {url}")
        url = Url(url = url)

        handler = url.get_handler()
        response = url.get_response()

        properties = url.get_social_properties()
        print(properties)

        return handler, response

    def test_crawlers(self):
        _, _, response = self.call_crawler(test_webpage, "RequestsCrawler")
        self.assertTrue(response.is_valid())

        _, _, response = self.call_crawler(test_webpage, "CurlCffiCrawler")
        self.assertTrue(response.is_valid())

        _, _, response = self.call_crawler("https://www.youtube.com/@LinusTechTips", "CurlCffiCrawler")
        self.assertTrue(response.is_valid())

        _, _, response = self.call_crawler(test_webpage, "HttpxCrawler")
        self.assertTrue(response.is_valid())

        _, _, response = self.call_crawler(test_webpage, "HttpMorphCrawler")
        self.assertTrue(response.is_valid())

        _, _, response = self.call_crawler(test_webpage, "StealthRequestsCrawler")
        self.assertTrue(response.is_valid())

        _, _, response = self.call_crawler(test_webpage, "SeleniumChromeHeadless")
        self.assertTrue(response.is_valid())

        _, _, response = self.call_crawler(test_webpage, "SeleniumChromeFull")
        self.assertTrue(response.is_valid())

        _, _, response = self.call_crawler(test_webpage, "SeleniumUndetected")
        self.assertTrue(response.is_valid())

        #_, _, response = self.call_crawler(test_webpage, "SeleniumWireFull")
        #self.assertTrue(response.is_valid())

        _, _, response = self.call_process("crawleebeautifulsoup.py")
        # _, _, response = self.call_crawleeplaywright()

    def test_crawl_script(self):
        _, _, response = self.call_process("crawl.py", "https://www.youtube.com/watch?v=9yanqmc01ck")
        self.assertTrue(response.is_valid())

        _, _, response = self.call_process("crawl.py", "https://www.youtube.com/feeds/videos.xml?channel_id=UCXuqSBlHAE6Xw-yeJA0Tunw")
        self.assertTrue(response.is_valid())

        _, _, response = self.call_process("crawl.py", "https://www.youtube.com/channel/UCXuqSBlHAE6Xw-yeJA0Tunw")
        self.assertTrue(response.is_valid())

        _, _, response = self.call_process("crawl.py", "https://www.youtube.com/@LinusTechTips")
        self.assertTrue(response.is_valid())

    def test_vanilla_google(self):
        handler, response = self.call_url(url = "https://www.google.com")

        self.assertEqual(handler.__class__.__name__, "HttpPageHandler")
        self.assertEqual(response.request.crawler_type.__class__.__name__, "CurlCffiCrawler")

        self.assertTrue(handler.get_title())
        self.assertTrue(len(handler.get_streams()) == 1)
        self.assertTrue(len(handler.get_feeds()) == 0)
        self.assertTrue(len(handler.get_entries()) == 0)

        self.assertTrue(response.is_valid())

    def test_youtube_video(self):
        handler, response = self.call_url(url = "https://www.youtube.com/watch?v=9yanqmc01ck")

        self.assertEqual(handler.__class__.__name__, "YouTubeVideoHandlerJson")
        self.assertEqual(response.request.crawler_type.__class__.__name__, "RequestsCrawler")

        self.assertTrue(handler.get_title())
        self.assertEqual(len(handler.get_streams()), 2)
        self.assertEqual(len(handler.get_feeds()), 1)
        self.assertTrue(len(handler.get_entries()) == 0)

        self.assertTrue(response.is_valid())

    def test_youtube_channel__feed(self):
        handler, response = self.call_url(url = "https://www.youtube.com/feeds/videos.xml?channel_id=UCXuqSBlHAE6Xw-yeJA0Tunw")

        self.assertEqual(handler.__class__.__name__, "YouTubeChannelHandlerJson")
        self.assertEqual(response.request.crawler_type.__class__.__name__, "RequestsCrawler")

        self.assertTrue(handler.get_title())
        self.assertTrue(len(handler.get_streams()) == 2)
        self.assertTrue(len(handler.get_feeds()) == 1)
        self.assertTrue(len(handler.get_entries()) > 0)

        self.assertTrue(response.is_valid())

    def test_youtube_channel__id(self):
        handler, response = self.call_url(url = "https://www.youtube.com/channel/UCXuqSBlHAE6Xw-yeJA0Tunw")

        self.assertEqual(handler.__class__.__name__, "YouTubeChannelHandlerJson")
        self.assertEqual(response.request.crawler_type.__class__.__name__, "RequestsCrawler")

        self.assertTrue(handler.get_title())
        self.assertTrue(len(handler.get_streams()) == 2)
        self.assertTrue(len(handler.get_feeds()) == 1)
        self.assertTrue(len(handler.get_entries()) > 0)

        self.assertTrue(response.is_valid())

    def test_youtube_channel__name(self):
        handler, response = self.call_url(url = "https://www.youtube.com/@LinusTechTips")

        self.assertEqual(handler.__class__.__name__, "YouTubeChannelHandlerJson")
        self.assertEqual(response.request.crawler_type.__class__.__name__, "RequestsCrawler")

        self.assertTrue(handler.get_title())
        self.assertEqual(handler.get_title(), "Linus Tech Tips")
        self.assertEqual(len(handler.get_streams()), 2)
        self.assertEqual(len(handler.get_feeds()), 1)
        self.assertTrue(len(handler.get_entries()) > 0)

        self.assertTrue(response.is_valid())

    def test_github(self):
        handler, response = self.call_url(url = "https://www.github.com/rumca-js/Internet-Places-Database")

        self.assertEqual(handler.__class__.__name__, "GitHubUrlHandler")
        self.assertEqual(response.request.crawler_type.__class__.__name__, "CurlCffiCrawler")

        self.assertTrue(handler.get_title())
        self.assertTrue(len(handler.get_streams()) == 1)
        self.assertTrue(len(handler.get_feeds()) == 2)
        self.assertTrue(len(handler.get_entries()) == 0)

        self.assertTrue(response.is_valid())

    def test_reddit__channel(self):
        handler, response = self.call_url(url = "https://www.reddit.com/r/wizardposting")

        self.assertEqual(handler.__class__.__name__, "RedditUrlHandler")
        self.assertEqual(response.request.crawler_type.__class__.__name__, "CurlCffiCrawler")

        self.assertTrue(handler.get_title())
        self.assertTrue(len(handler.get_streams()) == 2)
        self.assertTrue(len(handler.get_feeds()) == 1)
        self.assertTrue(len(handler.get_entries()) == 0)

        self.assertTrue(response.is_valid())

    def test_reddit__post(self):
        handler, response = self.call_url(url = "https://www.reddit.com/r/wizardposting/comments/1olomjs/screw_human_skeletons_im_gonna_get_more_creative/")

        self.assertEqual(handler.__class__.__name__, "RedditUrlHandler")
        self.assertEqual(response.request.crawler_type.__class__.__name__, "CurlCffiCrawler")

        self.assertTrue(handler.get_title())
        self.assertTrue(len(handler.get_streams()) == 2)
        self.assertTrue(len(handler.get_feeds()) == 1)
        self.assertTrue(len(handler.get_entries()) == 0)

        self.assertTrue(response.is_valid())
