from datetime import datetime
from rsshistory.webtools import (
    Url,
    PageOptions,
    HtmlPage,
    PageResponseObject,
    HttpPageHandler,
)
from rsshistory.configuration import Configuration

from tests.fakeinternet import FakeInternetTestCase, MockRequestCounter


class ScriptServerTest(FakeInternetTestCase):
    def setUp(self):
        self.disable_web_pages()

    def test_get_crawler(self):
        # call tested function
        crawler = Configuration().get_crawler("SeleniumChromeFull")
        self.assertTrue(crawler)

    def test_get_crawler_config(self):
        # call tested function
        config = Configuration().get_crawler_config()
        self.assertTrue(config)

    def test_is_allowed(self):
        config = Configuration()
        config.data["allowed_ids"] = "admin"

        # call tested function
        self.assertTrue(config.is_allowed("admin"))
        # call tested function
        self.assertFalse(config.is_allowed(""))
        # call tested function
        self.assertFalse(config.is_allowed(None))

        config.data["allowed_ids"] = []
        # call tested function
        self.assertTrue(config.is_allowed("admin"))
        # call tested function
        self.assertTrue(config.is_allowed(""))
