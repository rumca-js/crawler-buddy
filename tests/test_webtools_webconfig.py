from rsshistory.webtools import (
    WebConfig,
)

from .fakeinternet import FakeInternetTestCase, MockRequestCounter


class WebConfigTest(FakeInternetTestCase):
    def setUp(self):
        self.disable_web_pages()

    def test_get_browsers(self):
        browsers = WebConfig.get_browsers()
        self.assertTrue(len(browsers) > 0)

        self.assertIn("RequestsCrawler", browsers)

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

        self.assertIn("name", config)
        self.assertIn("crawler", config)
        self.assertIn("settings", config)

    def test_get_bytes_limits(self):
        limit = WebConfig.get_bytes_limit()

        self.assertTrue(limit)
