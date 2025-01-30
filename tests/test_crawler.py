from datetime import datetime
from rsshistory.webtools import (
    Url,
    PageOptions,
    HtmlPage,
    PageResponseObject,
    HttpPageHandler,
)
from rsshistory.crawler import Crawler

from tests.fakeinternet import FakeInternetTestCase, MockRequestCounter


class CrawlerTest(FakeInternetTestCase):
    def setUp(self):
        self.disable_web_pages()

    def test_get_page_url__by_name(self):
        crawler = Crawler()

        test_url = "https://linkedin.com"

        crawler_data = {
                "name" : "RequestsCrawler",
                "settings" : {
                    "timeout_s" : 20,
                    "remote_server": "https://",
                }
        }

        # call tested function
        page_url = crawler.get_page_url(test_url, crawler_data)
        self.assertTrue(page_url)

        self.assertIn("name", page_url.settings)
        self.assertEqual(page_url.settings["name"], "RequestsCrawler")

        self.assertIn("crawler", page_url.settings)
        self.assertEqual(type(page_url.settings["crawler"]).__name__, "RequestsCrawler")

    def test_get_page_url__by_crawler(self):
        crawler = Crawler()

        test_url = "https://linkedin.com"

        crawler_data = {
                "crawler" : "RequestsCrawler",
                "settings" : {
                    "timeout_s" : 20,
                    "remote_server": "https://",
                }
        }

        # call tested function
        page_url = crawler.get_page_url(test_url, crawler_data)
        self.assertTrue(page_url)

        self.assertIn("name", page_url.settings)
        self.assertEqual(page_url.settings["name"], "RequestsCrawler")

        self.assertIn("crawler", page_url.settings)
        self.assertEqual(type(page_url.settings["crawler"]).__name__, "RequestsCrawler")

    def test_get_page_url__invalid(self):
        crawler = Crawler()

        test_url = "https://linkedin.com"

        crawler_data = {
                "name" : "RequestsCrawlerDupa",
                "crawler" : "RequestsCrawlerDupa",
                "settings" : {
                    "timeout_s" : 20,
                    "remote_server": "https://",
                }
        }

        # call tested function
        page_url = crawler.get_page_url(test_url, crawler_data)
        self.assertFalse(page_url)

    def test_get_page_url__by_both(self):
        crawler = Crawler()

        test_url = "https://linkedin.com"

        crawler_data = {
                "name" : "RequestsCrawler",
                "crawler" : "RequestsCrawler",
                "settings" : {
                    "timeout_s" : 20,
                    "remote_server": "https://",
                }
        }

        # call tested function
        page_url = crawler.get_page_url(test_url, crawler_data)
        self.assertTrue(page_url)

        self.assertIn("name", page_url.settings)
        self.assertEqual(page_url.settings["name"], "RequestsCrawler")

        self.assertIn("crawler", page_url.settings)
        self.assertEqual(type(page_url.settings["crawler"]).__name__, "RequestsCrawler")

    def test_get_page_url__by_none(self):
        crawler = Crawler()

        test_url = "https://linkedin.com"

        crawler_data = {
                "settings" : {
                    "timeout_s" : 20,
                    "remote_server": "https://",
                }
        }

        # call tested function
        page_url = crawler.get_page_url(test_url, crawler_data)
        self.assertTrue(page_url)

        self.assertIn("name", page_url.settings)
        self.assertEqual(page_url.settings["name"], "DefaultCrawler")

        self.assertIn("crawler", page_url.settings)
        self.assertEqual(type(page_url.settings["crawler"]).__name__, "DefaultCrawler")
