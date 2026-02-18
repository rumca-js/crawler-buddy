from src.webtools import (
    WebConfig,
)

from utils.memorychecker import MemoryChecker
from src.entryrules import EntryRules
from src.configuration import Configuration

from tests.unit.fakeinternet import FakeInternetTestCase, MockRequestCounter


class WebConfigTest(FakeInternetTestCase):
    def setUp(self):
        self.disable_web_pages()

        rules = EntryRules()
        configuration = Configuration()

        self.memory_checker = MemoryChecker()
        self.memory_checker.get_memory_increase()

    def tearDown(self):
        memory_increase = self.memory_checker.get_memory_increase()
        self.assertEqual(memory_increase, 0)

    def test_get_crawler_names(self):
        crawlers = WebConfig.get_crawler_names()
        self.assertTrue(len(crawlers) > 0)
        self.assertIn("RequestsCrawler", crawlers)

    def test_get_crawlers(self):
        crawlers = WebConfig.get_crawlers()
        self.assertTrue(len(crawlers) > 0)

    def test_get_init_crawler_config__standard(self):
        config = WebConfig.get_init_crawler_config()
        self.assertTrue(len(config) > 0)

    def test_get_init_crawler_config(self):
        crawler = WebConfig.get_crawler_from_string("RequestsCrawler")
        self.assertTrue(crawler)

        crawler = WebConfig.get_crawler_from_string("SeleniumChromeHeadless")
        self.assertTrue(crawler)

        crawler = WebConfig.get_crawler_from_string("StealthRequestsCrawler")
        self.assertTrue(crawler)

    def test_get_default_crawler(self):
        config = WebConfig.get_default_crawler("https://test.com")

        self.assertIn("crawler_name", config)
        self.assertIn("settings", config)

    def test_get_bytes_limits(self):
        limit = WebConfig.get_bytes_limit()

        self.assertTrue(limit)
