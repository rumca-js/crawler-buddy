from rsshistory.webtools import (
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
