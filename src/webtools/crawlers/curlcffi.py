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
    WebToolsTimeoutException,
    HTTP_STATUS_CODE_EXCEPTION,
    HTTP_STATUS_CODE_CONNECTION_ERROR,
    HTTP_STATUS_CODE_SERVER_ERROR,
    HTTP_STATUS_CODE_TIMEOUT,
    WebLogger,
)

class CurlCffiCrawler(CrawlerInterface):
    """
    Python curl_cffi requests
    """

    def run_internal(self):
        """
        Run crawler
        """
        if not self.is_valid():
            self.add_error("Crawler is not valid")
            return self.response

        from curl_cffi.requests.exceptions import ConnectionError, Timeout

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

        except ConnectionError as E:
            self.set_connection_error_response()
        except Timeout as E:
            self.set_timeout_response()
        except WebToolsTimeoutException as E:
            self.set_timeout_response()
            self.response = PageResponseObject(
                self.request.url,
                text=None,
                status_code=HTTP_STATUS_CODE_TIMEOUT,
                request_url=self.request.url,
            )
            self.add_error("Url:{} Timeout".format(self.request.url))
        except Exception as E:
            self.set_exception_response(E)
            WebLogger.exc(E)

        try:
            if answer:
                answer.close()
        except Exception as E:
            pass

        return self.response

    def crawl_with_thread_implementation(self, request):
        import curl_cffi
        from curl_cffi import requests
        from curl_cffi.requests.exceptions import ConnectionError, Timeout

        headers = self.get_request_headers()
        impersonate = self.get_impersonate()

        proxies = self.request.get_proxies_map()

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

    def update_request(self):
        self.request.timeout_s = self.get_timeout_s()

    def get_impersonate(self):
        if self.request.settings:
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
            self.add_error(str(E))
            print(str(E))
            return False
