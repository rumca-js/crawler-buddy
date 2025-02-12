from src.webtools import (
    Url,
    RemoteServer,
)

from tests.fakeinternet import FakeInternetTestCase, MockRequestCounter


class RemoteServerTest(FakeInternetTestCase):
    def setUp(self):
        self.disable_web_pages()

    def test_get_response(self):
        url = Url("https://linkedin.com")
        all_properties = url.get_properties(full=True)

        server= RemoteServer("")

        # call tested function
        response = server.get_response(all_properties)

        self.assertTrue(response)
        self.assertTrue(response.get_text())
        self.assertEqual(response.get_status_code(), 200)
