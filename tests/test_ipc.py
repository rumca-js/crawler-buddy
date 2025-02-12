from src.webtools.ipc import *
from src.webtools import get_response_from_bytes

from .fakeinternet import FakeInternetTestCase


class TestBytes(FakeInternetTestCase):
    def test_string_to_command(self):
        # call tested function
        google_bytes = string_to_command("url", "https://google.com")
        # call tested function
        timeout_bytes = string_to_command("timeout", "20")

        total_bytes = bytearray()
        total_bytes.extend(google_bytes)
        total_bytes.extend(timeout_bytes)

        # call tested function
        commands = commands_from_bytes(total_bytes)
        self.assertEqual(len(commands), 2)

        self.assertEqual(commands[0][0], "url")
        self.assertEqual(commands[0][1].decode(), "https://google.com")

        self.assertEqual(commands[1][0], "timeout")
        self.assertEqual(commands[1][1].decode(), "20")

    def test_get_response_from_bytes(self):
        bytes1 = string_to_command("PageResponseObject.url", "https://google.com")
        bytes2 = string_to_command("PageResponseObject.status_code", "201")
        bytes3 = string_to_command("PageResponseObject.text", "page text")
        bytes4 = string_to_command(
            "PageResponseObject.headers", '{"Content-Type" : "text/html"}'
        )

        total_bytes = bytearray()
        total_bytes.extend(bytes1)
        total_bytes.extend(bytes2)
        total_bytes.extend(bytes3)
        total_bytes.extend(bytes4)

        response = get_response_from_bytes(total_bytes)

        self.assertEqual(response.url, "https://google.com")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.text, "page text")
