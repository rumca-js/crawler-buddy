"""
Script that can be used for debuggin server, checking connection
"""

import socket
import argparse
import json
from datetime import datetime, timedelta

from .webtools import PageRequestObject, PageResponseObject, get_request_to_bytes
from .ipc import SocketConnection, DEFAULT_PORT


max_transaction_timeout_s = 40


class ScrapingResponseHandler(object):
    def on_response(self, response):
        print("Received response:{}".format(response))


class ScrapingClient(object):
    def __init__(
        self, host=None, port=None, response_handler=None, scraping_script=None
    ):
        if host:
            self.host = host
        else:
            self.host = SocketConnection.gethostname()

        if port:
            self.port = port
        else:
            self.port = DEFAULT_PORT

        if scraping_script:
            self.scraping_script = scraping_script
        else:
            self.scraping_script = "poetry run python crawleebeautifulsoup.py"

        if response_handler:
            self.response_handler = response_handler
        else:
            self.response_handler = ScrapingResponseHandler()

    def set_scraping_script(self, script):
        self.scraping_script = script

    def connect(self):
        self.c = SocketConnection()
        if not self.c.connect(SocketConnection.gethostname(), self.port):
            return False
        else:
            return True

    def serve_forever(self):
        message = ""
        while message.lower().strip() != "bye":
            message = input(" -> ")

            try:
                if message.startswith("http"):
                    response = self.send_request_for_url(message)
                elif message == "help":
                    print("Supported commands:")
                    print(" - commands.debug")
                else:
                    self.send_command_string(message, "OK")
            except Exception as E:
                print("Exception:{}".format(str(E)))
                break

        self.close()

    def close(self):
        self.c.close()

    def is_closed(self):
        return self.c.is_closed()

    def send_request_for_url(self, url, timeout_s=30):
        request = PageRequestObject(url)
        request.timeout_s = timeout_s

        return self.send_request(request)

    def send_command_string(self, command, message):
        self.c.send_command_string(command, message)

        while True:
            command_data = self.c.get_command_and_data()
            if command_data:
                if command_data[0] == "debug.__init__":
                    pass
                elif command_data[0] == "debug.requests":
                    print("Requests len:{}".format(command_data[1].decode()))
                if command_data[0] == "debug.__del__":
                    return

    def send_request(self, request):
        response = PageResponseObject()
        time_start = datetime.now()

        bytes = get_request_to_bytes(request, self.scraping_script)
        self.c.send(bytes)

        while True:
            command_data = self.c.get_command_and_data()
            if command_data:
                # response

                if command_data[0] == "PageResponseObject.__init__":
                    pass
                elif command_data[0] == "PageResponseObject.url":
                    response.url = command_data[1].decode()
                elif command_data[0] == "PageResponseObject.headers":
                    try:
                        response.headers = json.loads(command_data[1].decode())
                    except ValueError as E:
                        print(str(E))

                elif command_data[0] == "PageResponseObject.status_code":
                    try:
                        response.status_code = int(command_data[1].decode())
                    except ValueError as E:
                        print(str(E))

                elif command_data[0] == "PageResponseObject.text":
                    response.set_text(command_data[1].decode())
                elif command_data[0] == "PageResponseObject.request_url":
                    response.request_url = command_data[1].decode()
                elif command_data[0] == "PageResponseObject.__del__":
                    self.c.send_command_string("commands.close", "OK")
                    self.response_handler.on_response(response)
                    return response

                # other commands

                elif command_data[0] == "debug.requests":
                    print("Requests len:{}".format(command_data[1].decode()))

                else:
                    print("Unsupported command:{}".format(command_data[0]))
                    break

            if self.c.is_closed():
                break

            # normal scenario - there is no command from server

            diff = datetime.now() - time_start

            if diff.total_seconds() > max_transaction_timeout_s:
                print("Could not obtain data in time limit")
                break


class ScrapingClientParser(object):
    """
    Headers can only be passed by input binary file
    """

    def parse(self):
        self.parser = argparse.ArgumentParser(description="Script server")
        self.parser.add_argument("--port", type=int, help="Port")
        self.parser.add_argument("-o", "--output-file", help="Response binary file")

        self.args = self.parser.parse_args()

        self.host = socket.gethostname()

        if "port" in self.args and self.args.port:
            self.port = self.args.port
        else:
            self.port = DEFAULT_PORT

    def is_valid(self):
        return True


def main():
    p = ScrapingClientParser()
    p.parse()

    c = ScrapingClient(p.host, p.port)
    c.set_scraping_script("poetry run python crawleebeautifulsoup.py")
    if not c.connect():
        print("Could not connect")
        return

    message = ""
    while message.lower().strip() != "exit":
        message = input(" -> ")
        if message.startswith("http"):
            response = c.send_request_for_url(message)
        else:
            c.send_command_string(message, "OK")

        print("Received response:{}".format(response))

        if c.is_closed():
            print("Client has closed")
            return


if __name__ == "__main__":
    main()
