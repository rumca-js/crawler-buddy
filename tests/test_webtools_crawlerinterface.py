from src.webtools import (
   CrawlerInterface,
)

from tests.fakeinternet import FakeInternetTestCase, MockRequestCounter, TestResponseObject


class CrawlerInterfaceTest(FakeInternetTestCase):
    def setUp(self):
        self.disable_web_pages()

    def test_constructor__user_agent(self):
        crawler = None
        url = "https://test.com"
        response_file = None

        settings = {}
        settings["name"] = "Test"
        settings["crawler"] = "Crawler"
        settings["headers"] = {}
        settings["headers"]["User-Agent"] = "Test-User-Agent"
        settings["settings"] = {}

        crawler = CrawlerInterface(request=None, url=url, response_file=None, settings=settings)

        self.assertIn("User-Agent", crawler.get_request_headers())
        self.assertEqual(crawler.get_request_headers()["User-Agent"], "Test-User-Agent")

    def test_constructor__get_accept_types(self):
        crawler = None
        url = "https://test.com"
        response_file = None

        settings = {}
        settings["name"] = "Test"
        settings["crawler"] = "Crawler"
        settings["settings"] = {}
        settings["settings"]["accept_content_types"] = "text/html,application/xhtml+xml,application/xml,application/rss;q=0.9,*/*;q=0.8"

        crawler = CrawlerInterface(request=None, url=url, response_file=None, settings=settings)

        self.assertIn("Accept", crawler.get_request_headers())
        self.assertIn("accept_content_types", crawler.settings["settings"])

        self.assertEqual(sorted(crawler.get_accept_types()), ['application', 'html', 'rss', 'text', 'xhtml', 'xml'])

    def test_constructor__timeout_s(self):
        crawler = None
        url = "https://test.com"
        response_file = None

        settings = {}
        settings["name"] = "Test"
        settings["crawler"] = "Crawler"
        settings["settings"] = {}
        settings["settings"]["timeout_s"] = 120

        crawler = CrawlerInterface(request=None, url=url, response_file=None, settings=settings)

        self.assertEqual(crawler.timeout_s, 120)

    def test_is_response_valid__true(self):
        crawler = None
        url = "https://test.com"
        response_file = None

        settings = {}
        settings["name"] = "Test"
        settings["crawler"] = "Crawler"
        settings["settings"] = {}
        settings["settings"]["Accept"] = "text/html,application/xhtml+xml,application/xml,application/rss;q=0.9,*/*;q=0.8"

        crawler = CrawlerInterface(request=None, url=url, response_file=None, settings=settings)

        crawler.response = TestResponseObject(url, {}, 20)

        self.assertTrue(crawler.is_response_valid())

    def test_is_response_valid__false(self):
        crawler = None
        url = "https://test.com"
        response_file = None

        settings = {}
        settings["name"] = "Test"
        settings["crawler"] = "Crawler"
        settings["settings"] = {}
        settings["settings"]["accept_content_types"] = "text/html,application/xhtml+xml,application/xml,application/rss;q=0.9,*/*;q=0.8"

        crawler = CrawlerInterface(request=None, url=url, response_file=None, settings=settings)

        crawler.response = TestResponseObject(url, {}, 20)
        crawler.response.headers.headers["Content-Type"] = "jpeg"

        self.assertFalse(crawler.is_response_valid())
