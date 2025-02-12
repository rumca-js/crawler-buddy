from datetime import datetime
from src.webtools import (
    Url,
    PageOptions,
    HtmlPage,
    PageResponseObject,
    HttpPageHandler,
    RemoteServer,
)

from tests.fakeinternet import FakeInternetTestCase, MockRequestCounter


class RemoteServerTest(FakeInternetTestCase):
    def setUp(self):
        self.disable_web_pages()

    def test_read_properties_section(self):
        server = RemoteServer("http://example.com")

        all_data = {
                "success" : False,
                "error" : "Somethings wrong",
        }

        # call tested function
        response = server.read_properties_section("Response", all_data)

        self.assertFalse(response)
