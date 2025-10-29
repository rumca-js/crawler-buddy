from webtoolkit import RemoteServer

from src.webtools import (
    Url,
)
from script_server import set_response_impl

from tests.fakeinternet import FakeInternetTestCase, MockRequestCounter, FlaskRequest


class ScriptServerTest(FakeInternetTestCase):
    def setUp(self):
        self.disable_web_pages()

    def test_set_response_impl(self):
        request = FlaskRequest("http://192.168.0.0")

        crawler_data = {
          "name" : "MockCrawler",
          "timeout_s" : 400,
          "settings" : {
              "script": "test/path",
          }
        }

        request.json = {
            "request_url" : "https://google.com",
            "Contents" : "<html>",
            "status_code" : 200,
            "Headers" : {
                "Content-Type" : "text/html",
            },
            "crawler_data" : crawler_data,
        }

        # call tested function
        url = set_response_impl(request)

        self.assertTrue(url)

        all_properties = url.get_properties(full=True)

        self.assertTrue(all_properties)

        properties = RemoteServer.read_properties_section("Properties", all_properties)
        self.assertIn("link", properties)
        self.assertEqual(properties["link"], "https://google.com")

        text = RemoteServer.read_properties_section("Text", all_properties)
        self.assertIn("Contents", text)

        headers = RemoteServer.read_properties_section("Headers", all_properties)
        self.assertIn("Content-Type", headers)
        self.assertEqual(headers["Content-Type"], "text/html")

        request_data = RemoteServer.read_properties_section("Request", all_properties)
        self.assertIn("url", request_data)
        self.assertIn("crawler_name", request_data)
        self.assertEqual(request_data["url"], "https://google.com")
        self.assertEqual(request_data["crawler_name"], "MockCrawler")

        response = RemoteServer.read_properties_section("Response", all_properties)
        self.assertIn("status_code", response)
        self.assertEqual(response["status_code"], 200)
