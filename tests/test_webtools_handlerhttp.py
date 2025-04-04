from src.webtools import (
   HttpPageHandler,
   HtmlPage,
   RssPage,
   Url,
)

from tests.fakeinternet import FakeInternetTestCase, MockRequestCounter, YouTubeJsonHandlerMock


class HttpPageHandlerTest(FakeInternetTestCase):
    def setUp(self):
        self.disable_web_pages()

    def test_constructor(self):
        test_link = "https://linkedin.com"
        settings = Url(test_link).get_init_settings()

        # call tested function
        handler = HttpPageHandler(test_link, settings = settings, url_builder = Url)

        self.assertTrue(handler)

    def test_get_page_handler__html(self):
        test_link = "https://linkedin.com"
        settings = Url(test_link).get_init_settings()

        handler = HttpPageHandler(test_link, settings = settings, url_builder = Url)

        # call tested function
        self.assertTrue(type(handler.get_page_handler()), HtmlPage)

    def test_get_page_handler__rss(self):
        test_link = "https://www.reddit.com/r/searchengines/.rss"
        settings = Url(test_link).get_init_settings()

        handler = HttpPageHandler(test_link, settings = settings, url_builder = Url)

        # call tested function
        self.assertTrue(type(handler.get_page_handler()), RssPage)

    def test_get_page_handler__broken_content_type(self):
        test_link = "https://rss-page-with-broken-content-type.com/feed"
        settings = Url(test_link).get_init_settings()

        handler = HttpPageHandler(test_link, settings = settings, url_builder = Url)
        response = handler.get_response()

        # call tested function
        self.assertTrue(type(handler.get_page_handler()), RssPage)

        self.assertEqual(response.get_content_type(), "text/html")

    def test_get_contents_hash(self):
        test_link = "https://linkedin.com"
        settings = Url(test_link).get_init_settings()

        handler = HttpPageHandler(test_link, settings = settings, url_builder = Url)

        # call tested function
        hash = handler.get_contents_hash()

        self.assertTrue(hash)

    def test_get_contents_body_hash(self):
        test_link = "https://linkedin.com"
        settings = Url(test_link).get_init_settings()

        handler = HttpPageHandler(test_link, settings = settings, url_builder = Url)

        # call tested function
        hash = handler.get_contents_body_hash()

        self.assertTrue(hash)

    def test_get_contents__html(self):
        test_link = "https://linkedin.com"
        settings = Url(test_link).get_init_settings()

        handler = HttpPageHandler(test_link, settings = settings, url_builder = Url)

        # call tested function
        self.assertTrue(handler.get_contents())

    def test_get_response__html(self):
        test_link = "https://linkedin.com"
        settings = Url(test_link).get_init_settings()

        handler = HttpPageHandler(test_link, settings = settings, url_builder = Url)

        # call tested function
        self.assertTrue(handler.get_response())

    def test_is_handled_by(self):
        test_link = "http://linkedin.com"

        # call tested function
        handler = HttpPageHandler(test_link, url_builder = Url)

        self.assertTrue(handler.is_handled_by())

        test_link = "https://linkedin.com"

        # call tested function
        handler = HttpPageHandler(test_link, url_builder = Url)

        self.assertTrue(handler.is_handled_by())

        test_link = "ftp://linkedin.com"

        # call tested function
        handler = HttpPageHandler(test_link, url_builder = Url)

        self.assertFalse(handler.is_handled_by())

    def test_get_feeds__reddit(self):
        test_link = "https://www.reddit.com/r/searchengines"
        settings = Url(test_link).get_init_settings()

        handler = HttpPageHandler(test_link, settings = settings, url_builder = Url)

        # call tested function
        self.assertIn("https://www.reddit.com/r/searchengines/.rss", handler.get_feeds())

    def test_get_feeds__github(self):
        test_link = "https://github.com/rumca-js/Django-link-archive"
        settings = Url(test_link).get_init_settings()

        handler = HttpPageHandler(test_link, settings = settings, url_builder = Url)

        # call tested function
        self.assertIn("https://github.com/rumca-js/Django-link-archive/commits.atom", handler.get_feeds())
