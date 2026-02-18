from datetime import datetime
from webtoolkit import  (
    HtmlPage,
    PageRequestObject,
    PageResponseObject,
    HttpPageHandler,
)
from webtoolkit.tests.fakeresponse import FlaskRequest

from src.webtools import (
    Url,
)
from src.crawler import Crawler
from src.entryrules import EntryRules
from utils.memorychecker import MemoryChecker

from tests.unit.fakeinternet import FakeInternetTestCase, MockRequestCounter


class EntryRuleseTest(FakeInternetTestCase):
    def setUp(self):
        self.disable_web_pages()

        rules = EntryRules()

        self.memory_checker = MemoryChecker()
        self.memory_checker.get_memory_increase()

    def tearDown(self):
        memory_increase = self.memory_checker.get_memory_increase()
        self.assertEqual(memory_increase, 0)
        print(f"Memory increase: {memory_increase}")

    def test_is_url_hit__wildcards(self):
        rules = EntryRules()
        self.assertEqual(rules.entry_rules["entryrules"][0]["browser"], "SeleniumChromeFull")
        rules.entry_rules["entryrules"][0]["rule_url"] = ".*x.com.*"

        rule = rules.entry_rules["entryrules"][0]

        # call tested function
        self.assertTrue(rules.is_url_hit(rule, "http://x.com"))
        # call tested function
        self.assertTrue(rules.is_url_hit(rule, "https://x.com"))
        # call tested function
        self.assertTrue(rules.is_url_hit(rule, "https://xacom"))
        # call tested function
        self.assertTrue(rules.is_url_hit(rule, "smb://x.com"))

        # call tested function
        self.assertFalse(rules.is_url_hit(rule, "http://b.com"))

    def test_is_url_hit__wildcards_protocol(self):
        rules = EntryRules()
        self.assertEqual(rules.entry_rules["entryrules"][0]["browser"], "SeleniumChromeFull")
        rules.entry_rules["entryrules"][0]["rule_url"] = ".*://x.com.*"

        rule = rules.entry_rules["entryrules"][0]

        # call tested function
        self.assertTrue(rules.is_url_hit(rule, "http://x.com"))
        # call tested function
        self.assertTrue(rules.is_url_hit(rule, "https://x.com"))
        # call tested function
        self.assertTrue(rules.is_url_hit(rule, "smb://x.com"))

        # call tested function
        self.assertFalse(rules.is_url_hit(rule, "http://b.com"))

    def test_is_url_hit__wildcards_dot_com(self):
        rules = EntryRules()
        self.assertEqual(rules.entry_rules["entryrules"][0]["browser"], "SeleniumChromeFull")
        rules.entry_rules["entryrules"][0]["rule_url"] = ".*x\.com.*"

        rule = rules.entry_rules["entryrules"][0]

        # call tested function
        self.assertTrue(rules.is_url_hit(rule, "http://x.com"))
        # call tested function
        self.assertTrue(rules.is_url_hit(rule, "https://x.com"))
        # call tested function
        self.assertTrue(rules.is_url_hit(rule, "smb://x.com"))

        # call tested function
        self.assertFalse(rules.is_url_hit(rule, "http://b.com"))
        # call tested function
        self.assertFalse(rules.is_url_hit(rule, "https://xacom"))

    def test_get_request_data__by_entry_rule_wildcards(self):
        rules = EntryRules()
        self.assertEqual(rules.entry_rules["entryrules"][0]["browser"], "SeleniumChromeFull")
        rules.entry_rules["entryrules"][0]["rule_url"] = ".*x.com.*"

        test_url = "https://x.com"

        crawler_data = """{
                "settings" : {
                    "timeout_s" : 20,
                    "remote_server": "https://"
                }
        }"""

        browser = rules.get_browser("https://x.com")
        self.assertEqual(browser, "SeleniumChromeFull")
