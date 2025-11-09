import time
import threading
import urllib.parse

from webtoolkit import (
    PageResponseObject,
    CrawlerInterface,
    HTTP_STATUS_CODE_CONNECTION_ERROR,
    HTTP_STATUS_CODE_SERVER_ERROR,
)

class StealthRequestsCrawler(CrawlerInterface):
    """
    Python steath requests
    """

    def run(self):
        if not self.is_valid():
            return

        self.response = PageResponseObject(
            self.request.url,
            text=None,
            status_code=HTTP_STATUS_CODE_SERVER_ERROR,
            request_url=self.request.url,
        )

        answer = self.build_requests()

        content = None
        text = None

        if answer:
            content = answer.content
            text = answer.text

        if answer and content:
            self.response = PageResponseObject(
                self.request.url,
                binary=content,
                status_code=answer.status_code,
                request_url=self.request.url,
                headers=answer.headers,
            )

            if not self.is_response_valid():
                return self.response

        elif answer and text:
            self.response = PageResponseObject(
                self.request.url,
                binary=None,
                text=text,
                status_code=answer.status_code,
                request_url=self.request.url,
                headers=answer.headers,
            )

        elif answer:
            self.response = PageResponseObject(
                self.request.url,
                binary=None,
                text=None,
                status_code=answer.status_code,
                request_url=self.request.url,
                headers=answer.headers,
            )

            return self.response

        if self.response:
            return self.response

    def build_requests(self):
        import stealth_requests as requests

        try:
            answer = requests.get(
                self.request.url,
                timeout=self.get_timeout_s(),
                verify=self.request.ssl_verify,
                # stream=True,   # TODO does not work with it
            )
            return answer
        except Exception as E:
            self.response = PageResponseObject(
                self.request.url,
                text=None,
                status_code=HTTP_STATUS_CODE_CONNECTION_ERROR,
                request_url=self.request.url,
            )
            self.response.add_error("Url:{} Connection error".format(self.request.url))

    def is_valid(self):
        try:
            import stealth_requests as requests

            return True
        except Exception as E:
            print(str(E))
            return False
