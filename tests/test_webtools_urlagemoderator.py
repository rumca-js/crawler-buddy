from src.webtools import (
   RssPage,
   HtmlPage,
   YouTubeVideoHandler,
   UrlAgeModerator
)
from .fakeinternet import FakeInternetTestCase


class UrlAgeModeratorTest(FakeInternetTestCase):
    def setUp(self):
        self.disable_web_pages()

    def test_is_valid_pass(self):
        properties = {}
        properties["title"] = "Test title"
        properties["description"] = "Test description"

        keywords = []

        v = UrlAgeModerator(properties=properties)

        # call tested function
        self.assertEqual(v.get_age(), None)

    def test_is_valid_blocked(self):
        properties = {}
        properties["title"] = "lestbian bisexual fuck"
        properties["description"] = "Test description"

        v = UrlAgeModerator(properties=properties)

        # call tested function
        self.assertTrue(v.get_age(), 15)
