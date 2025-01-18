from datetime import datetime
from rsshistory.webtools import (
    Url,
    PageOptions,
    HtmlPage,
    PageResponseObject,
    HttpPageHandler,
)
from script_server import *

from tests.fakeinternet import FakeInternetTestCase, MockRequestCounter


class ScriptServerTest(FakeInternetTestCase):
    def setUp(self):
        self.disable_web_pages()

    def test_get_crawler(self):
        # call tested function
        crawler = get_crawler("SeleniumChromeFull")
        self.assertTrue(crawler)

    def test_get_crawler_config(self):
        # call tested function
        config = get_crawler_config()
        self.assertTrue(config)
