"""
Provides botasaurus crawler implementation.
https://github.com/omkarcloud/botasaurus
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


class BotasaurusCrawler(CrawlerInterface):
    """
    Web crawler using Botasaurus
    """

    def run(self):
        """
        Runs crawler.
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
            result = self.build_browser_request()

            if not result:
                return self.response

            html = result.get("html")
            status_code = result.get("status_code", 200)
            headers = result.get("headers", {})

            self.response = PageResponseObject(
                self.request.url,
                text=html,
                status_code=status_code,
                request_url=self.request.url,
                headers=headers,
            )

            if not self.is_response_valid():
                return self.response

            return self.response

        except Exception as e:
            self.response = PageResponseObject(
                self.request.url,
                text=None,
                status_code=HTTP_STATUS_CODE_CONNECTION_ERROR,
                request_url=self.request.url,
            )
            self.response.add_error(
                f"Url: {str(e)} Cannot render or fetch with Botasaurus"
            )
            return self.response

    def build_browser_request(self):
        from botasaurus import bts

        """
        Launch Botasaurus and retrieve HTML content
        """

        @bts.default
        def get_html(driver):
            driver.get(self.request.url)
            html = driver.page_source
            return {
                "html": html,
                "status_code": 200,  # Botsaurus doesn't expose this, assume OK
                "headers": {},  # You could mock or skip headers if irrelevant
            }

        return get_html()

    def is_valid(self) -> bool:
        """
        Returns indication if crawler is available
        """
        try:
            from botasaurus import bts

            return True
        except Exception as E:
            print(str(E))
            return False
