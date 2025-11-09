import time
import threading
import urllib.parse

from webtoolkit import (
    PageResponseObject,
    CrawlerInterface,
    HTTP_STATUS_CODE_CONNECTION_ERROR,
    HTTP_STATUS_CODE_SERVER_ERROR,
)

class HttpxCrawler(CrawlerInterface):
    """
    Python httpx
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

        if answer:
            self.response = PageResponseObject(
                self.request.url,
                status_code=answer.status_code,
                request_url=self.request.url,
                headers=answer.headers,
            )
            if not self.is_response_valid():
                return self.response

        content = getattr(answer, "content", None)
        text = getattr(answer, "text", None)

        if answer and content:
            self.response = PageResponseObject(
                self.request.url,
                binary=content,
                status_code=answer.status_code,
                request_url=self.request.url,
                headers=answer.headers,
            )

            return self.response

        elif text:
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

        if self.response:
            return self.response

    def build_requests(self):
        import httpx

        try:
            answer = httpx.get(
                self.request.url,
                timeout=self.get_timeout_s(),
                verify=self.request.ssl_verify,
                headers=self.get_request_headers(),
                cookies=self.request.cookies,
                follow_redirects=True,
                # stream=True, # TODO
            )
            return answer
        except Exception as E:
            self.response = PageResponseObject(
                self.request.url,
                text=None,
                status_code=HTTP_STATUS_CODE_CONNECTION_ERROR,
                request_url=self.request.url,
            )
            self.response.add_error("Url:{} Cannot create request".format(str(E)))

    def is_valid(self):
        try:
            import httpx

            return True
        except Exception as E:
            print(str(E))
            return False
