import argparse
import requests
import json

from webtoolkit import (
  PageRequestObject,
  CrawlerInterface,
  response_to_json,
  file_to_request,
  RemoteUrl,
  WebLogger,
)


class ScriptCrawlerParser(object):
    """
    Headers can only be passed by input binary file
    """

    def parse(self):
        self.parser = argparse.ArgumentParser(description="Data analyzer program")
        self.parser.add_argument("--url", help="Directory to be scanned")
        self.parser.add_argument(
            "--timeout", default=10, type=int, help="Timeout expressed in seconds"
        )
        self.parser.add_argument("--ssl-verify", default=False, help="SSL verify")
        self.parser.add_argument("--accept-types", help="Accept types")
        self.parser.add_argument("--respect-robots", default=False, help="Respect robots.txt")
        self.parser.add_argument("--bytes-limit", help="Bytes limit")

        self.parser.add_argument("--user-agent", help="Bytes limit")

        self.parser.add_argument("--settings", help="Settings map")
        self.parser.add_argument("--cookies", help="Cookies map")
        self.parser.add_argument("--request-headers", help="Fetch headers only")

        self.parser.add_argument("--ping", default=False, help="Ping only")

        self.parser.add_argument("--http-proxy", help="Proxy address")
        self.parser.add_argument("--https-proxy", help="Proxy address")

        self.parser.add_argument("--request-file", help="Input request file")
        self.parser.add_argument("--remote-server", help="Remote server")
        self.parser.add_argument("--crawl-id", help="Crawl id")
        self.parser.add_argument("-o", "--output-file", help="Response binary file")

        self.parser.add_argument("-v", "--verbose", action="store_true", help="Verbose")

        self.args = self.parser.parse_args()

    def is_valid(self):
        if "output_file" not in self.args:
            print("Output file not in args")
            return False

        if self.args.request_file is None and self.args.url is None:
            print("Url file not in args")
            return False

        return True

    def get_request(self):
        if self.args.request_file:
            r = file_to_request(self.args.request_file)
            if r:
                return r

        r = PageRequestObject(self.args.url)

        r.timeout_s = self.args.timeout
        r.ssl_verify = self.args.ssl_verify
        r.respect_robots = self.args.respect_robots
        r.accept_types = self.args.accept_types
        r.bytes_limit = self.args.bytes_limit

        r.http_proxy = self.args.http_proxy
        r.https_proxy = self.args.https_proxy

        r.user_agent = self.args.user_agent
        r.ping = self.args.ping
        r.request_headers = self.args.request_headers
        r.settings = self.args.settings

        if not r.settings:
            r.settings = {}
        if not r.cookies:
            r.cookies = {}

        return r

    def save(self, response):
        if response:
            if self.args.remote_server:
                crawl_id = None
                if self.args.crawl_id:
                    crawl_id = self.args.crawl_id

                    self.post(response, "crawl_id={crawl_id}")
                elif response and response.request:
                    url = response.request.url
                    crawler_name = response.request.crawler_name
                    handler_name = response.request.handler_name
                    self.post(response, f"url={url}&crawler_name={crawler_name}&handler_name={handler_name}")

    def post(self, response, args):
        response_json = response_to_json(response)

        remote_server = self.args.remote_server

        url = f"{remote_server}/set?{args}"
        try:
            response = requests.post(url, json=response_json)
        except Exception as E:
            WebLogger.exc(E, str(response_json))
