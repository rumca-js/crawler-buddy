from src.webtools import (
    UrlPropertyValidator,
    YouTubeVideoHandler,
)

from .fakeinternet import FakeInternetTestCase


class UrlHandlerTest(FakeInternetTestCase):
    def setUp(self):
        self.disable_web_pages()

    def test_is_valid_pass(self):
        properties = {}
        properties["title"] = "Test title"

        keywords = []

        v = UrlPropertyValidator(properties=properties, blocked_keywords=keywords)

        # call tested function
        self.assertTrue(v.is_valid())

    def test_is_valid_blocked(self):
        properties = {}
        properties["title"] = "renegat0x0 site"

        keywords = ["renegat0x0 site"]

        v = UrlPropertyValidator(properties=properties, blocked_keywords=keywords)

        # call tested function
        self.assertTrue(not v.is_valid())
