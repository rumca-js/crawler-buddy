"""
httpmorph crawler implmementation
https://github.com/arman-bd/httpmorph
"""
import time
import threading
import urllib.parse

from webtoolkit import (
    PageResponseObject,
    CrawlerInterface,
    HTTP_STATUS_CODE_EXCEPTION,
    HTTP_STATUS_CODE_CONNECTION_ERROR,
    HTTP_STATUS_CODE_SERVER_ERROR,
    HTTP_STATUS_CODE_TIMEOUT,
)

class HttpMorphCrawler(CrawlerInterface):
    """
    Python httpmorph requests
    """

    def run(self):
        """
        Runs crawler
        """
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
        import httpmorph

        self.update_request()

        try:
            answer = httpmorph.get(
                url=self.request.url,
                timeout=self.request.timeout_s,
                verify=self.request.ssl_verify,
                cookies=self.request.cookies,
                #impersonate="chrome",
                #headers=headers,
                # stream=True, # TODO
            )
            return answer

        except httpmorph.ConnectionError as E:
            self.response = PageResponseObject(
                self.request.url,
                text=None,
                status_code=HTTP_STATUS_CODE_CONNECTION_ERROR,
                request_url=self.request.url,
            )
            self.response.add_error("Url:{} Cannot create request".format(str(E)))

        except httpmorph.Timeout as E:
            self.response = PageResponseObject(
                self.request.url,
                text=None,
                status_code=HTTP_STATUS_CODE_TIMEOUT,
                request_url=self.request.url,
            )
            self.response.add_error("Url:{} Timeout".format(str(E)))

        except Exception as E:
            self.response = PageResponseObject(
                self.request.url,
                text=None,
                status_code=HTTP_STATUS_CODE_EXCEPTION,
                request_url=self.request.url,
            )
            self.response.add_error("Url:{} Cannot create request".format(str(E)))

    def update_request(self):
        self.request.timeout_s = self.get_timeout_s()

    def is_valid(self) -> bool:
        """
        Returns information if crawler is available
        """
        try:
            import httpmorph

            return True
        except Exception as E:
            return False
