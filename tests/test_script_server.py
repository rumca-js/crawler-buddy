from src.webtools import (
    Url,
    RemoteServer,
)
from script_server import set_response_impl

from tests.fakeinternet import FakeInternetTestCase, MockRequestCounter

class FlaskArgs(object):
    def __init__(self):
        self._map = {}

    def get(self, key):
        if key in self._map:
            return self._map[key]

    def set(self, key, value):
        self._map[key] = value


class FlaskRequest(object):
    def __init__(self, host):
        self.host = host
        self.args = FlaskArgs()
        self.json = None

    def set(self, key, value):
        self.args.set(key, value)


class ScriptServerTest(FakeInternetTestCase):
    def setUp(self):
        self.disable_web_pages()

    def test_set_response_impl(self):
        request = FlaskRequest("http://192.168.0.0")

        crawler_data = {
          "name" : "test name",
          "crawler" : "ScriptCrawler",
          "settings" : {
              "timeout_s" : 400,
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

        remote = RemoteServer("")

        properties = remote.read_properties_section("Properties", all_properties)
        self.assertIn("link", properties)
        self.assertEqual(properties["link"], "https://google.com")

        text = remote.read_properties_section("Text", all_properties)
        self.assertIn("Contents", text)

        headers = remote.read_properties_section("Headers", all_properties)
        self.assertIn("Content-Type", headers)
        self.assertEqual(headers["Content-Type"], "text/html")

        settings = remote.read_properties_section("Settings", all_properties)
        self.assertIn("crawler", settings)
        self.assertIn("name", settings)

        response = remote.read_properties_section("Response", all_properties)
        self.assertIn("status_code", response)
        self.assertEqual(response["status_code"], 200)
