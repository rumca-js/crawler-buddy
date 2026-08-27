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

import gc
import time
import subprocess
import unittest
from pathlib import Path

from webtoolkit.utils.memorychecker import MemoryChecker

from webtoolkit import file_to_response
import webtoolkit
from src.webtools import Url
from src.webtools.webconfig import WebConfig


# change test webpage to see if other pages can be scraped using different scrapers
test_webpage = "https://google.com"


class TestMemoryUrl(unittest.TestCase):
    def setUp(self):
        WebConfig.use_print_logging()

        self.memory_checker = MemoryChecker()
        memory_increase = self.memory_checker.get_memory_increase()
        self.ignore_memory = False
        self.num_iterations = 100

    def tearDown(self):
        gc.collect()

        if not self.ignore_memory:
            memory_increase = self.memory_checker.get_memory_increase()
            self.assertTrue(memory_increase < 40)

    def call_url(self, url):
        start_time = time.time()

        url = Url(url = url)

        handler = url.get_handler()
        response = url.get_response()

        return response, handler, url

    def test_vanilla_google(self):
        for i in range(1, self.num_iterations):
            test_url = "https://www.google.com"
            response, handler, url = self.call_url(test_url)
            if response and not response.is_valid():
                print("Response is invalid")
            url.close()

    def test_reddit__channel(self):
        """
        """
        for i in range(1, self.num_iterations):
            test_url = "https://www.reddit.com/r/wizardposting"
            response, handler, url = self.call_url(test_url)
            if response and not response.is_valid():
                print("Response is invalid")
            url.close()

    def test_github(self):
        """
        """
        for i in range(1, self.num_iterations):
            test_url = "https://github.com/rumca-js/crawler-buddy"
            response, handler, url = self.call_url(test_url)
            if response and not response.is_valid():
                print("Response is invalid")
            url.close()

    def test_youtube_channel_by_id(self):
        for i in range(1, self.num_iterations):
            test_url = "https://www.youtube.com/channel/UCXuqSBlHAE6Xw-yeJA0Tunw"
            response, handler, url = self.call_url(test_url)
            if response and not response.is_valid():
                print("Response is invalid")
            url.close()

    def test_social_data__youtube_channel_id(self):
        for i in range(1, self.num_iterations):
            test_url = "https://www.youtube.com/channel/UCXuqSBlHAE6Xw-yeJA0Tunw"
            url = Url(url = test_url)
            social = url.get_social_properties()
            url.close()
