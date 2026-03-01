"""
Httpx crawler implementation
https://github.com/luminati-io/httpx-web-scraping
"""
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
    Python httpx crawler
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

        try:
            answer = self.build_requests()

            if answer:
                self.response = PageResponseObject(
                    self.request.url,
                    status_code=answer.status_code,
                    request_url=self.request.url,
                    headers=answer.headers,
                )
                if not self.is_response_valid():
                    answer.close()
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

        except Exception as E:
            self.response = PageResponseObject(
                self.request.url,
                text=None,
                status_code=HTTP_STATUS_CODE_CONNECTION_ERROR,
                request_url=self.request.url,
            )
            self.response.add_error("Url:{} Cannot create request".format(str(E)))

        try:
            if answer:
                answer.close()
        except Exception as E:
            pass

        return self.response

    def crawl_with_thread_implementation(self, request):
        import httpx

        proxy=None
        if self.request.http_proxy:
            proxy = self.request.http_proxy
        if self.request.https_proxy:
            proxy = self.request.https_proxy

            answer = httpx.get(
                self.request.url,
                timeout=self.request.timeout_s,
                verify=self.request.ssl_verify,
                headers=self.request.request_headers,
                proxy=proxy,
                cookies=self.request.cookies,
                follow_redirects=True,
                # stream=True, # TODO
            )
            return answer

    def update_request(self):
        self.request.timeout_s = self.get_timeout_s()
        self.request.request_headers = self.get_request_headers()

    def is_valid(self) -> bool:
        """
        Returns information if crawler is valid
        """
        try:
            import httpx

            return True
        except Exception as E:
            print(str(E))
            return False
