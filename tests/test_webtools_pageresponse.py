from src.webtools import (
    PageResponseObject,
    response_to_json,
    json_to_response,
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

    def test_get_encoding__quotes(self):
        headers = {"Content-Type": 'text/html; charset="UTF-8"'}
        response = PageResponseObject(
            "https://test.com", "", status_code=200, headers=headers
        )

        self.assertEqual(response.get_encoding(), "UTF-8")

    def test_get_encoding__no_quotes(self):
        headers = {"Content-Type": "text/html; charset=UTF-8"}
        response = PageResponseObject(
            "https://test.com", "", status_code=200, headers=headers
        )

        self.assertEqual(response.get_encoding(), "UTF-8")

    def test_is_content__html(self):
        headers = {"Content-Type": "text/html; charset=UTF-8"}
        response = PageResponseObject(
            "https://test.com", "", status_code=200, headers=headers
        )

        self.assertTrue(response.is_content_html())
        self.assertFalse(response.is_content_rss())

    def test_is_content__rss(self):
        headers = {"Content-Type": "text/rss; charset=UTF-8"}
        response = PageResponseObject(
            "https://test.com", "", status_code=200, headers=headers
        )

        self.assertTrue(response.is_content_rss())
        self.assertFalse(response.is_content_html())

    def test_get_hash__text(self):
        headers = {"Content-Type": "text/rss; charset=UTF-8"}
        response = PageResponseObject(
            "https://test.com", "", status_code=200, text="test", headers=headers
        )

        self.assertTrue(response.get_hash())

    def test_get_hash__binary(self):
        headers = {"Content-Type": "text/rss; charset=UTF-8"}
        response = PageResponseObject(
            "https://test.com", status_code=200, binary=b"test", headers=headers
        )

        self.assertTrue(response.get_hash())


class PageResponseToJsonTest(FakeInternetTestCase):
    def setUp(self):
        self.disable_web_pages()

    def test_response_to_json__403_no_text(self):
        headers = {"Content-Type": "text/rss; charset=UTF-8"}
        response = PageResponseObject(
            "https://test.com", "", status_code=403, headers=headers
        )

        # call tested function
        json_map = response_to_json(response)

        self.assertTrue(json_map)
        self.assertIn("is_valid", json_map)
        self.assertIn("status_code", json_map)
        self.assertIn("status_code_str", json_map)
        self.assertIn("crawl_time_s", json_map)
        self.assertIn("Content-Type", json_map)
        self.assertIn("Recognized-Content-Type", json_map)
        self.assertIn("Content-Length", json_map)
        self.assertIn("Charset", json_map)
        self.assertIn("hash", json_map)
        self.assertIn("body_hash", json_map)
        self.assertNotIn("streams", json_map)

        self.assertEqual(json_map["is_valid"], True)
        self.assertEqual(json_map["status_code"], 403)
        self.assertEqual(json_map["Content-Type"], "text/rss; charset=UTF-8")
        self.assertEqual(json_map["Recognized-Content-Type"], "text/rss")
        self.assertEqual(json_map["Charset"], "UTF-8")
        self.assertEqual(json_map["hash"], None)
        self.assertEqual(json_map["body_hash"], None)

    def test_response_to_json__404_no_text(self):
        headers = {"Content-Type": "text/rss; charset=UTF-8"}
        response = PageResponseObject(
            "https://test.com", "", status_code=404, headers=headers
        )

        # call tested function
        json_map = response_to_json(response)

        self.assertTrue(json_map)
        self.assertIn("is_valid", json_map)
        self.assertIn("status_code", json_map)
        self.assertIn("status_code_str", json_map)
        self.assertIn("crawl_time_s", json_map)
        self.assertIn("Content-Type", json_map)
        self.assertIn("Recognized-Content-Type", json_map)
        self.assertIn("Content-Length", json_map)
        self.assertIn("Charset", json_map)
        self.assertIn("hash", json_map)
        self.assertIn("body_hash", json_map)
        self.assertNotIn("streams", json_map)

        self.assertEqual(json_map["is_valid"], False)
        self.assertEqual(json_map["status_code"], 404)
        self.assertEqual(json_map["Content-Type"], "text/rss; charset=UTF-8")
        self.assertEqual(json_map["Recognized-Content-Type"], "text/rss")
        self.assertEqual(json_map["Charset"], "UTF-8")
        self.assertEqual(json_map["hash"], None)
        self.assertEqual(json_map["body_hash"], None)

    def test_response_to_json__valid_text_no_streams(self):
        headers = {"Content-Type": "text/rss; charset=UTF-8"}
        response = PageResponseObject(
            "https://test.com", "", status_code=200, text="test", headers=headers
        )

        # call tested function
        json_map = response_to_json(response)

        self.assertTrue(json_map)
        self.assertIn("is_valid", json_map)
        self.assertIn("status_code", json_map)
        self.assertIn("status_code_str", json_map)
        self.assertIn("crawl_time_s", json_map)
        self.assertIn("Content-Type", json_map)
        self.assertIn("Recognized-Content-Type", json_map)
        self.assertIn("Content-Length", json_map)
        self.assertIn("Charset", json_map)
        self.assertIn("hash", json_map)
        self.assertIn("body_hash", json_map)
        self.assertNotIn("streams", json_map)

        self.assertEqual(json_map["is_valid"], True)
        self.assertEqual(json_map["status_code"], 200)
        self.assertEqual(json_map["Content-Type"], "text/rss; charset=UTF-8")
        self.assertEqual(json_map["Recognized-Content-Type"], "text/rss")
        self.assertEqual(json_map["Charset"], "UTF-8")
        self.assertNotEqual(json_map["hash"], None)
        self.assertEqual(json_map["body_hash"], None)

    def test_response_to_json__valid_text_streams(self):
        headers = {"Content-Type": "text/rss; charset=UTF-8"}
        response = PageResponseObject(
            "https://test.com", "", status_code=200, text="test", headers=headers
        )

        # call tested function
        json_map = response_to_json(response, with_streams=True)

        self.assertTrue(json_map)
        self.assertIn("is_valid", json_map)
        self.assertIn("status_code", json_map)
        self.assertIn("status_code_str", json_map)
        self.assertIn("crawl_time_s", json_map)
        self.assertIn("Content-Type", json_map)
        self.assertIn("Recognized-Content-Type", json_map)
        self.assertIn("Content-Length", json_map)
        self.assertIn("Charset", json_map)
        self.assertIn("hash", json_map)
        self.assertIn("body_hash", json_map)
        self.assertIn("streams", json_map)

        self.assertEqual(json_map["is_valid"], True)
        self.assertEqual(json_map["status_code"], 200)
        self.assertEqual(json_map["Content-Type"], "text/rss; charset=UTF-8")
        self.assertEqual(json_map["Recognized-Content-Type"], "text/rss")
        self.assertEqual(json_map["Charset"], "UTF-8")
        self.assertNotEqual(json_map["hash"], None)
        self.assertEqual(json_map["body_hash"], None)


class JsonToPageResponseTest(FakeInternetTestCase):
    def setUp(self):
        self.disable_web_pages()

    def test__valid(self):
        json_data = {
            "status_code" : 200,
        }

        response = json_to_response(json_data)
        self.assertTrue(response.is_valid())

    def test__not_valid(self):
        json_data = {
            "status_code" : 404,
        }

        response = json_to_response(json_data)
        self.assertFalse(response.is_valid())

    def test__url(self):
        json_data = {
            "url" : "https://test.com",
        }

        response = json_to_response(json_data)
        self.assertEqual(response.url, "https://test.com")

    def test__request_url(self):
        json_data = {
            "request_url" : "https://test.com",
        }

        response = json_to_response(json_data)
        self.assertEqual(response.request_url, "https://test.com")

    def test__text(self):
        json_data = {
            "text" : "<html></html>",
        }

        response = json_to_response(json_data)
        self.assertEqual(response.text, "<html></html>")

    def test__headers(self):
        json_data = {
            "headers" : {
                "Content-Type" : "test/content/type",
            }
        }

        response = json_to_response(json_data)
        self.assertEqual(response.get_content_type(), "test/content/type")
