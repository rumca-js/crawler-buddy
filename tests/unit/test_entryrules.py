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

from tests.unit.fakeinternet import FakeInternetTestCase, MockRequestCounter
from webtoolkit.tests.fakeresponse import FlaskRequest


class EntryRuleseTest(FakeInternetTestCase):
    def setUp(self):
        self.disable_web_pages()

    def test_get_request_data__by_entry_rule(self):
        rules = EntryRules()
        self.assertEqual(rules.entry_rules["entryrules"][0]["browser"], "SeleniumChromeFull")
        rules.entry_rules["entryrules"][0]["rule_url"] = "https://x.com"

        test_url = "https://x.com"

        crawler_data = """{
                "settings" : {
                    "timeout_s" : 20,
                    "remote_server": "https://"
                }
        }"""

        browser = rules.get_browser("https://x.com")
        self.assertEqual(browser, "SeleniumChromeFull")
