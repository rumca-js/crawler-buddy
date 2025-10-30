from datetime import datetime
from webtoolkit import  (
    HtmlPage,
    PageRequestObject,
    PageResponseObject,
    HttpPageHandler,
)
from src.webtools import (
    Url,
)
from src.crawler import Crawler
from src.entryrules import EntryRules

from tests.fakeinternet import FakeInternetTestCase, MockRequestCounter, FlaskRequest


class CrawlerTest(FakeInternetTestCase):
    def setUp(self):
        self.disable_web_pages()

    def test_get_request_data__by_name(self):
        crawler = Crawler()

        request = FlaskRequest("http://192.168.0.0")
        request.set("url", "https://test.com")
        request.set("crawler_name", "RequestsCrawler")

        # call tested function
        page_request = crawler.get_request_data(request)

        self.assertEqual(page_request.crawler_name, "RequestsCrawler")

    def test_get_request_data__crawler_data(self):
        crawler = Crawler()

        crawler_data = """{
           "crawler_name": "RequestsCrawler"
        }"""

        request = FlaskRequest("http://192.168.0.0")
        request.set("url", "https://test.com")
        request.set("crawler_data", crawler_data)

        # call tested function
        page_request = crawler.get_request_data(request)

        self.assertTrue(page_request)
        self.assertEqual(page_request.crawler_name, "RequestsCrawler")
        self.assertEqual(type(page_request.crawler_type).__name__, "RequestsCrawler")

    def test_get_request_data__invalid(self):
        crawler = Crawler()

        test_url = "https://linkedin.com"

        crawler_data = """{
           "crawler_name" : "RequestsCrawlerDupa",
           "crawler_type" : "RequestsCrawlerDupa",
           "timeout_s" : 20,
           "remote_server": "https://"
        }"""

        request = FlaskRequest("http://192.168.0.0")
        request.set("url", "https://test.com")
        request.set("crawler_data", crawler_data)

        # call tested function
        page_request = crawler.get_request_data(request)
        self.assertFalse(page_request)

    def test_get_request_data__by_none(self):
        crawler = Crawler()

        test_url = "https://linkedin.com"

        crawler_data = """{
           "timeout_s" : 20
        }"""

        request = FlaskRequest("http://192.168.0.0")
        request.set("url", "https://test.com")
        request.set("crawler_data", crawler_data)

        # call tested function
        page_request = crawler.get_request_data(request)

        self.assertTrue(page_request)
        self.assertEqual(page_request.crawler_name, "MockCrawler")

        self.assertEqual(type(page_request.crawler_type).__name__, "MockCrawler")
        self.assertEqual(page_request.timeout_s, 20)

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
        page_request = crawler.get_request_data(request)

        self.assertTrue(page_request)
        self.assertEqual(page_request.crawler_name, "SeleniumChromeFull")

        self.assertEqual(type(page_request.crawler_type).__name__, "SeleniumChromeFull")

    def test_get_request_data__crawler_data__ssl_verify_True(self):
        crawler = Crawler()

        crawler_data = """{
           "crawler_name": "RequestsCrawler",
           "crawler_type": "RequestsCrawler",
           "ssl_verify": true,
           "respect_robots": true
        }"""

        request = FlaskRequest("http://192.168.0.0")
        request.set("url", "https://test.com")
        request.set("crawler_data", crawler_data)

        # call tested function
        page_request = crawler.get_request_data(request)

        self.assertTrue(page_request)
        self.assertEqual(page_request.crawler_name, "RequestsCrawler")
        self.assertEqual(type(page_request.crawler_type).__name__, "RequestsCrawler")
        self.assertEqual(page_request.ssl_verify, True)
        self.assertEqual(page_request.respect_robots, True)
        self.assertEqual(page_request.timeout_s, None)

    def test_get_request_data__crawler_data__ssl_verify_False(self):
        crawler = Crawler()

        crawler_data = """{
           "crawler_name": "RequestsCrawler",
           "crawler_type": "RequestsCrawler",
           "ssl_verify" : false,
           "respect_robots" : false,
           "timeout_s" : 60,
           "delay_s" : 10
        }"""

        request = FlaskRequest("http://192.168.0.0")
        request.set("url", "https://test.com")
        request.set("crawler_data", crawler_data)

        # call tested function
        page_request = crawler.get_request_data(request)

        self.assertTrue(page_request)
        self.assertEqual(page_request.crawler_name, "RequestsCrawler")
        self.assertEqual(type(page_request.crawler_type).__name__, "RequestsCrawler")
        self.assertEqual(page_request.ssl_verify, False)
        self.assertEqual(page_request.respect_robots, False)
        self.assertEqual(page_request.timeout_s, 60)
        self.assertEqual(page_request.delay_s, 10)

    def test_get_request_data__default_bytes_limit(self):
        crawler = Crawler()

        crawler_data = """{
            "crawler_name": "RequestsCrawler",
            "crawler_type": "RequestsCrawler",
            "ssl_verify": true,
            "respect_robots": true
        }"""

        request = FlaskRequest("http://192.168.0.0")
        request.set("url", "https://test.com")
        request.set("crawler_data", crawler_data)

        # call tested function
        page_request = crawler.get_request_data(request)

        self.assertTrue(page_request)
        self.assertTrue(page_request.bytes_limit)

    def test_get_request_data__accept_types(self):
        crawler = Crawler()

        crawler_data = """{
                "crawler_name": "RequestsCrawler",
                "crawler_type": "RequestsCrawler",
                "ssl_verify": true,
                "respect_robots_txt": true
        }"""

        request = FlaskRequest("http://192.168.0.0")
        request.set("url", "https://test.com")
        request.set("crawler_data", crawler_data)

        # call tested function
        page_request = crawler.get_request_data(request)

        self.assertTrue(page_request)
        self.assertTrue(page_request.accept_types)

    def test_get_page_url__by_name(self):
        crawler = Crawler()

        test_url = "https://linkedin.com"

        request = PageRequestObject(test_url)
        request.crawler_name = "RequestsCrawler"
        request.crawler_type = "RequestsCrawler"
        request.timeout_s = 20

        # call tested function
        page_url = crawler.get_page_url(test_url, request=request)
        self.assertTrue(page_url)

        self.assertTrue(page_url.request)
        self.assertTrue(page_url.request.crawler_name)
        self.assertEqual(page_url.request.crawler_name, "RequestsCrawler")

    def test_get_all_properties(self):
        crawler = Crawler()

        test_url = "https://linkedin.com"

        request = FlaskRequest("http://192.168.0.0")
        request.set("url", test_url)
        request.set("crawler_name", "RequestsCrawler")

        self.assertEqual(crawler.url_history.get_size(), 0)
        self.assertEqual(crawler.queue.get_size(), 0)

        # call tested function
        props = crawler.get_all_properties(request)
        self.assertTrue(props)

        self.assertEqual(crawler.url_history.get_size(), 1)
        self.assertEqual(crawler.queue.get_size(), 0)

    def test_get_all_properties__from_history(self):
        crawler = Crawler()

        test_url = "https://linkedin.com"

        request = FlaskRequest("http://192.168.0.0")
        request.set("url", test_url)
        request.set("crawler_name", "RequestsCrawler")

        self.assertEqual(crawler.url_history.get_size(), 0)
        self.assertEqual(crawler.queue.get_size(), 0)

        # call tested function
        props = crawler.get_all_properties(request)
        self.assertTrue(props)

        self.assertEqual(crawler.url_history.get_size(), 1)
        self.assertEqual(crawler.queue.get_size(), 0)

        # call tested function
        props = crawler.get_all_properties(request)
        self.assertTrue(props)

        self.assertEqual(crawler.url_history.get_size(), 1) # no new history was created
        self.assertEqual(crawler.queue.get_size(), 0)
