
from datetime import datetime
from src.webtools import (
    ScriptCrawler,
)

from tests.fakeinternet import FakeInternetTestCase, MockRequestCounter


class ScriptCrawlerTest(FakeInternetTestCase):
    def setUp(self):
        self.disable_web_pages()

    def test_read_properties_section(self):
        crawler = ScriptCrawler(url = "https://google.com", script = "poetry run python crawlersunnyday.py")

        # call tested function
        response = crawler.run()

        self.assertTrue(response)
        self.assertEqual(response.url, "https://google.com")
        self.assertEqual(response.status_code, 200)
