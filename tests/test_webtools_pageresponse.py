from src.webtools import (
    PageResponseObject,
)

from tests.fakeinternet import FakeInternetTestCase, MockRequestCounter


class PageResponseObjectTest(FakeInternetTestCase):
    def setUp(self):
        self.disable_web_pages()

    def test_get_content_type(self):
        headers = {"Content-Type": "text/html"}
        response = PageResponseObject(
            "https://test.com", "", status_code=200, headers=headers
        )

        # call tested function
        self.assertEqual(response.get_content_type(), "text/html")

    def test_is_valid__true(self):
        headers = {"Content-Type": "text/html"}

        response = PageResponseObject(
            "https://test.com", "", status_code=200, headers=headers
        )

        # call tested function - ok status is OK
        self.assertTrue(response.is_valid())

        response = PageResponseObject(
            "https://test.com", "", status_code=300, headers=headers
        )
        # call tested function - redirect status is OK
        self.assertTrue(response.is_valid())

        response = PageResponseObject(
            "https://test.com", "", status_code=301, headers=headers
        )
        # call tested function - redirect status is OK
        self.assertTrue(response.is_valid())

        response = PageResponseObject(
            "https://test.com", "", status_code=304, headers=headers
        )
        # call tested function - redirect status is OK
        self.assertTrue(response.is_valid())

        response = PageResponseObject(
            "https://test.com", "", status_code=403, headers=headers
        )
        # call tested function
        self.assertTrue(response.is_valid())

    def test_is_valid__status(self):
        headers = {"Content-Type": "text/html"}
        response = PageResponseObject(
            "https://test.com", "", status_code=100, headers=headers
        )
        # call tested function
        self.assertFalse(response.is_valid())

        response = PageResponseObject(
            "https://test.com", "", status_code=400, headers=headers
        )
        # call tested function
        self.assertFalse(response.is_valid())

        response = PageResponseObject(
            "https://test.com", "", status_code=401, headers=headers
        )
        # call tested function
        self.assertFalse(response.is_valid())

        response = PageResponseObject(
            "https://test.com", "", status_code=402, headers=headers
        )
        # call tested function
        self.assertFalse(response.is_valid())

        response = PageResponseObject(
            "https://test.com", "", status_code=404, headers=headers
        )
        # call tested function
        self.assertFalse(response.is_valid())

        response = PageResponseObject(
            "https://test.com", "", status_code=405, headers=headers
        )
        # call tested function
        self.assertFalse(response.is_valid())

        response = PageResponseObject(
            "https://test.com", "", status_code=500, headers=headers
        )
        # call tested function
        self.assertFalse(response.is_valid())

    def test_is_headers_empty__true(self):
        headers = {}
        response = PageResponseObject(
            "https://test.com", "", status_code=200, headers=headers
        )

        self.assertTrue(response.is_headers_empty())

    def test_is_headers_empty__false(self):
        headers = {"Content-Type": "text/html"}
        response = PageResponseObject(
            "https://test.com", "", status_code=200, headers=headers
        )

        self.assertFalse(response.is_headers_empty())

    def test_get_charset__quotes(self):
        headers = {"Content-Type": 'text/html; charset="UTF-8"'}
        response = PageResponseObject(
            "https://test.com", "", status_code=200, headers=headers
        )

        self.assertEqual(response.get_content_type_charset(), "UTF-8")

    def test_get_charset__no_quotes(self):
        headers = {"Content-Type": "text/html; charset=UTF-8"}
        response = PageResponseObject(
            "https://test.com", "", status_code=200, headers=headers
        )

        self.assertEqual(response.get_content_type_charset(), "UTF-8")

    def test_is_content_html(self):
        headers = {"Content-Type": "text/html; charset=UTF-8"}
        response = PageResponseObject(
            "https://test.com", "", status_code=200, headers=headers
        )

        self.assertTrue(response.is_content_html())
        self.assertFalse(response.is_content_rss())

    def test_is_content_rss(self):
        headers = {"Content-Type": "text/rss; charset=UTF-8"}
        response = PageResponseObject(
            "https://test.com", "", status_code=200, headers=headers
        )

        self.assertTrue(response.is_content_rss())
        self.assertFalse(response.is_content_html())
