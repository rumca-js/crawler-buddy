"""
CurlCffi crawler implementation
https://github.com/lexiforest/curl_cffi
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

class CurlCffiCrawler(CrawlerInterface):
    """
    Python curl_cffi requests
    """

    def run(self):
        """
        Run crawler
        """
        self.response = PageResponseObject(
            self.request.url,
            text=None,
            status_code=HTTP_STATUS_CODE_SERVER_ERROR,
            request_url=self.request.url,
        )

        if not self.is_valid():
            self.response.add_error("Crawler is not valid")
            return self.response

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

        answer.close()

        if self.response:
            return self.response

    def build_requests(self):
        import curl_cffi
        from curl_cffi import requests
        from curl_cffi.requests.exceptions import ConnectionError, Timeout

        headers = self.get_request_headers()
        self.update_request()
        impersonate = self.get_impersonate()

        try:
            proxies = self.request.get_proxies_map()
            print(self.request)

            answer = curl_cffi.get(
                self.request.url,
                timeout=self.request.timeout_s,
                verify=self.request.ssl_verify,
                cookies=self.request.cookies,
                headers=self.request.request_headers,
                proxy=proxies,
                impersonate=impersonate,

                # stream=True, # TODO
            )
            return answer
        except ConnectionError as E:
            self.response = PageResponseObject(
                self.request.url,
                text=None,
                status_code=HTTP_STATUS_CODE_CONNECTION_ERROR,
                request_url=self.request.url,
            )
            self.response.add_error("Url:{} Cannot create request".format(str(E)))
        except Timeout as E:
            self.response = PageResponseObject(
                self.request.url,
                text=None,
                status_code=HTTP_STATUS_CODE_TIMEOUT,
                request_url=self.request.url,
            )
            self.response.add_error("Url:{} Cannot create request".format(str(E)))
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

    def get_impersonate(self):
        impersonate = self.request.settings.get("impersonate")
        if impersonate:
            return impersonate

        return "chrome"

    def is_valid(self) -> bool:
        """
        Returns indication if crawler is available
        """
        try:
            from curl_cffi import requests

            return True
        except Exception as E:
            if self.response:
                self.response.add_error(str(E))
            print(str(E))
            return False
