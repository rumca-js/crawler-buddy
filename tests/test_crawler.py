from datetime import datetime
from src.webtools import (
    Url,
    PageOptions,
    HtmlPage,
    PageResponseObject,
    HttpPageHandler,
)
from src.crawler import Crawler
from src.entryrules import EntryRules

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

    def test_get_request_data__by_name(self):
        crawler = Crawler()

        request = FlaskRequest("http://192.168.0.0")
        request.set("url", "https://test.com")
        request.set("name", "RequestsCrawler")

        # call tested function
        data = crawler.get_request_data(request)

        self.assertEqual(data["name"], "RequestsCrawler")

    def test_get_request_data__crawler(self):
        crawler = Crawler()

        request = FlaskRequest("http://192.168.0.0")
        request.set("url", "https://test.com")
        request.set("crawler", "RequestsCrawler")

        # call tested function
        data = crawler.get_request_data(request)

        self.assertEqual(type(data["crawler"]).__name__, "RequestsCrawler")

    def test_get_request_data__crawler_data(self):
        crawler = Crawler()

        crawler_data = """{
                "name": "RequestsCrawler",
                "crawler": "RequestsCrawler"
        }"""

        request = FlaskRequest("http://192.168.0.0")
        request.set("url", "https://test.com")
        request.set("crawler_data", crawler_data)

        # call tested function
        data = crawler.get_request_data(request)

        self.assertTrue(data)
        self.assertEqual(data["name"], "RequestsCrawler")
        self.assertEqual(type(data["crawler"]).__name__, "RequestsCrawler")

    def test_get_request_data__invalid(self):
        crawler = Crawler()

        test_url = "https://linkedin.com"

        crawler_data = """{
                "name" : "RequestsCrawlerDupa",
                "crawler" : "RequestsCrawlerDupa",
                "settings" : {
                    "timeout_s" : 20,
                    "remote_server": "https://"
                }
        }"""

        request = FlaskRequest("http://192.168.0.0")
        request.set("url", "https://test.com")
        request.set("crawler_data", crawler_data)

        # call tested function
        data = crawler.get_request_data(request)
        self.assertFalse(data)

    def test_get_request_data__by_none(self):
        crawler = Crawler()

        test_url = "https://linkedin.com"

        crawler_data = """{
                "settings" : {
                    "timeout_s" : 20,
                    "remote_server": "http://8.8.8.8:3000"
                }
        }"""

        request = FlaskRequest("http://192.168.0.0")
        request.set("url", "https://test.com")
        request.set("crawler_data", crawler_data)

        # call tested function
        data = crawler.get_request_data(request)

        self.assertTrue(data)
        self.assertIn("name", data)
        self.assertEqual(data["name"], "DefaultCrawler")

        self.assertIn("crawler", data)
        self.assertEqual(type(data["crawler"]).__name__, "DefaultCrawler")

        self.assertIn("settings", data)
        self.assertIn("timeout_s", data["settings"])
        self.assertIn("remote_server", data["settings"])

        self.assertEqual(data["settings"]["remote_server"], "http://8.8.8.8:3000")

        self.assertNotIn("timeout_s", data)

    def test_get_request_data__by_entry_rule(self):
        crawler = Crawler()

        rules = EntryRules()
        self.assertEqual(rules.entry_rules["entryrules"][0]["browser"], "SeleniumChromeFull")

        crawler.entry_rules = rules

        test_url = "https://x.com"

        crawler_data = """{
                "settings" : {
                    "timeout_s" : 20,
                    "remote_server": "https://"
                }
        }"""

        request = FlaskRequest("http://192.168.0.0")
        request.set("url", "https://x.com")
        request.set("crawler_data", crawler_data)

        # call tested function
        data = crawler.get_request_data(request)

        self.assertTrue(data)
        self.assertIn("name", data)
        self.assertEqual(data["name"], "SeleniumChromeFull")

        self.assertIn("crawler", data)
        self.assertEqual(type(data["crawler"]).__name__, "SeleniumChromeFull")

    def test_get_request_data__crawler_data__ssl_verify_True(self):
        crawler = Crawler()

        crawler_data = """{
                "name": "RequestsCrawler",
                "crawler": "RequestsCrawler",
                "settings": {
                   "ssl_verify": true,
                   "respect_robots_txt": true
                }
        }"""

        request = FlaskRequest("http://192.168.0.0")
        request.set("url", "https://test.com")
        request.set("crawler_data", crawler_data)

        # call tested function
        data = crawler.get_request_data(request)

        self.assertTrue(data)
        self.assertEqual(data["name"], "RequestsCrawler")
        self.assertEqual(type(data["crawler"]).__name__, "RequestsCrawler")
        self.assertEqual(data["settings"]["ssl_verify"], True)
        self.assertEqual(data["settings"]["respect_robots_txt"], True)

        self.assertIn("settings", data)
        self.assertIn("remote_server", data["settings"])

        self.assertNotIn("timeout_s", data)

    def test_get_request_data__crawler_data__ssl_verify_False(self):
        crawler = Crawler()

        crawler_data = """{
                "name": "RequestsCrawler",
                "crawler": "RequestsCrawler",
                "settings" : {
                   "ssl_verify" : false,
                   "respect_robots_txt" : false,
                   "timeout_s" : 60,
                   "delay_s" : 10
                }
        }"""

        request = FlaskRequest("http://192.168.0.0")
        request.set("url", "https://test.com")
        request.set("crawler_data", crawler_data)

        # call tested function
        data = crawler.get_request_data(request)

        self.assertTrue(data)
        self.assertEqual(data["name"], "RequestsCrawler")
        self.assertEqual(type(data["crawler"]).__name__, "RequestsCrawler")
        self.assertEqual(data["settings"]["ssl_verify"], False)
        self.assertEqual(data["settings"]["respect_robots_txt"], False)
        self.assertEqual(data["settings"]["timeout_s"], 60)
        self.assertEqual(data["settings"]["delay_s"], 10)

        self.assertNotIn("timeout_s", data)

    def test_get_request_data__bytes_limit(self):
        crawler = Crawler()

        crawler_data = """{
                "name": "RequestsCrawler",
                "crawler": "RequestsCrawler",
                "settings": {
                   "ssl_verify": true,
                   "respect_robots_txt": true
                }
        }"""

        request = FlaskRequest("http://192.168.0.0")
        request.set("url", "https://test.com")
        request.set("crawler_data", crawler_data)

        # call tested function
        data = crawler.get_request_data(request)

        self.assertTrue(data)
        self.assertTrue(data["settings"]["bytes_limit"])

    def test_get_request_data__accept_types(self):
        crawler = Crawler()

        crawler_data = """{
                "name": "RequestsCrawler",
                "crawler": "RequestsCrawler",
                "settings": {
                   "ssl_verify": true,
                   "respect_robots_txt": true
                }
        }"""

        request = FlaskRequest("http://192.168.0.0")
        request.set("url", "https://test.com")
        request.set("crawler_data", crawler_data)

        # call tested function
        data = crawler.get_request_data(request)

        self.assertTrue(data)
        self.assertIn("settings", data)
        self.assertNotIn("Accept", data["settings"])
        self.assertIn("accept_content_types", data["settings"])

        self.assertNotIn("timeout_s", data)

    def test_get_request_data__remote_server__default(self):
        crawler = Crawler()

        test_url = "https://linkedin.com"

        crawler_data = """{
                "settings" : {
                    "timeout_s" : 20
                }
        }"""

        request = FlaskRequest("http://192.168.0.0")
        request.set("url", "https://test.com")
        request.set("crawler_data", crawler_data)

        # call tested function
        data = crawler.get_request_data(request)

        self.assertTrue(data)
        self.assertIn("name", data)
        self.assertEqual(data["name"], "DefaultCrawler")

        self.assertIn("crawler", data)
        self.assertEqual(type(data["crawler"]).__name__, "DefaultCrawler")

        self.assertIn("settings", data)
        self.assertIn("timeout_s", data["settings"])
        self.assertIn("remote_server", data["settings"])

        self.assertEqual(data["settings"]["remote_server"], "http://127.0.0.1:3000")

        self.assertNotIn("timeout_s", data)

    def test_get_page_url__by_name(self):
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

