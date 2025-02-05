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

class FlaskArgs(object):
    def __init__(self):
        self._map = {}

    def get(self, key):
        if key in self._map:
            return self._map[key]

    def set(self, key, value):
        self._map[key] = value


class FlaskRequest(object):
    def __init__(self, host):
        self.host = host
        self.args = FlaskArgs()

    def set(self, key, value):
        self.args.set(key, value)


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

    def test_get_request_data__name(self):
        crawler = Crawler()

        request = FlaskRequest("http://192.168.0.0")
        request.set("name", "MMMMmm")

        data = crawler.get_request_data(request)

        self.assertEqual(data["name"], "MMMMmm")

    def test_get_request_data__crawler(self):
        crawler = Crawler()

        request = FlaskRequest("http://192.168.0.0")
        request.set("crawler", "MMMMmm")

        data = crawler.get_request_data(request)

        self.assertEqual(data["crawler"], "MMMMmm")

    def test_get_request_data__crawler_data(self):
        crawler = Crawler()

        crawler_data = """{
                "name": "Requests",
                "crawler": "RequestsCrawler"
        }"""

        request = FlaskRequest("http://192.168.0.0")
        request.set("crawler_data", crawler_data)

        data = crawler.get_request_data(request)

        self.assertEqual(data["name"], "Requests")
        self.assertEqual(data["crawler"], "RequestsCrawler")

    def test_get_request_data__crawler_data__ssl_verify_True(self):
        crawler = Crawler()

        crawler_data = """{
                "name": "Requests",
                "crawler": "RequestsCrawler",
                "settings": {
                   "ssl_verify": true,
                   "respect_robots_txt": true
                }
        }"""

        request = FlaskRequest("http://192.168.0.0")
        request.set("crawler_data", crawler_data)

        data = crawler.get_request_data(request)

        self.assertEqual(data["name"], "Requests")
        self.assertEqual(data["crawler"], "RequestsCrawler")
        self.assertEqual(data["settings"]["ssl_verify"], True)
        self.assertEqual(data["settings"]["respect_robots_txt"], True)

    def test_get_request_data__crawler_data__ssl_verify_False(self):
        crawler = Crawler()

        crawler_data = """{
                "name": "Requests",
                "crawler": "RequestsCrawler",
                "settings" : {
                   "ssl_verify" : false,
                   "respect_robots_txt" : false,
                   "timeout_s" : 60,
                   "delay_s" : 10
                }
        }"""

        request = FlaskRequest("http://192.168.0.0")
        request.set("crawler_data", crawler_data)

        data = crawler.get_request_data(request)

        self.assertEqual(data["name"], "Requests")
        self.assertEqual(data["crawler"], "RequestsCrawler")
        self.assertEqual(data["settings"]["ssl_verify"], False)
        self.assertEqual(data["settings"]["respect_robots_txt"], False)
        self.assertEqual(data["settings"]["timeout_s"], 60)
        self.assertEqual(data["settings"]["delay_s"], 10)
