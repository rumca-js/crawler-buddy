import subprocess
import json
import os
import traceback
from pathlib import Path

from urllib3.exceptions import InsecureRequestWarning
from urllib3 import disable_warnings
from datetime import timedelta

from utils.dateutils import DateUtils

from .webtools import (
    WebLogger,
    PageRequestObject,
    PageResponseObject,
    PageOptions,
    lazy_load_content,
    HTTP_STATUS_CODE_EXCEPTION,
    HTTP_STATUS_CODE_CONNECTION_ERROR,
    HTTP_STATUS_CODE_TIMEOUT,
    HTTP_STATUS_CODE_FILE_TOO_BIG,
    HTTP_STATUS_CODE_PAGE_UNSUPPORTED,
    HTTP_STATUS_CODE_SERVER_ERROR,
)
from .urllocation import UrlLocation
from .pages import (
    HtmlPage,
    RssPage,
    PageFactory,
)
from .handlerinterface import HandlerInterface
from .webconfig import WebConfig


class HttpRequestBuilder(object):
    """
    Should not contain any HTML/RSS content processing.
    This should be just a builder.

    It should not be called directly, nor used
    """

    # use headers from https://www.supermonitoring.com/blog/check-browser-http-headers/

    def __init__(self, url=None, settings=None, request=None, url_builder=None):
        """
        @param url URL
        @param contents URL page contents
        @param use_selenium decides if selenium is used
        """
        self.request = request
        self.response = None
        self.timeout_s = 10

        self.url = url
        self.settings = settings
        self.robots_contents = None

        # Flag to not retry same contents requests for things we already know are dead
        self.dead = False

        if self.url is None:
            stack_lines = traceback.format_stack()
            stack_str = "".join(stack_lines)

            WebLogger.error("Passed incorrect url {}".format(stack_str))
            return

        if self.url.lower().find("https") >= 0:
            self.protocol = "https"
        elif self.url.lower().find("http") >= 0:
            self.protocol = "http"
        else:
            self.protocol = "https"

        self.user_agent = None
        if request:
            if request.user_agent:
                self.user_agent = request.user_agent

        if not self.user_agent:
            self.user_agent = HttpPageHandler.user_agent

        self.headers = None
        if request:
            if request.request_headers:
                self.headers = request.request_headers

        if not self.headers:
            self.headers = {
                "User-Agent": self.user_agent,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Charset": "utf-8,ISO-8859-1;q=0.7,*;q=0.3",
                "Accept-Encoding": "none",
                "Accept-Language": "en-US,en;q=0.8",
                "Connection": "keep-alive",
            }

    def get_response(self):
        if self.response:
            return self.response

        if self.dead:
            return None

        self.get_response_implementation()

        return self.response

    def get_text(self):
        response = self.get_response()
        if response:
            return response.get_text()

    def get_binary(self):
        response = self.get_response()
        if response:
            return response.get_binary()

    def get_contents_internal(self, request):
        """
        There are 3 levels of scraping:
         - requests (fast)
         - if above fails we can use headless browser
         - if above fails we can use full browser (most advanced, resource consuming)

        First configured thing provides return value
        """
        crawler_data = self.settings

        if not crawler_data:
            return

        if "crawler" not in crawler_data:
            WebLogger.error("Url:{} No crawler in crawler data".format(request.url))
            return

        crawler = crawler_data["crawler"]

        WebLogger.debug(
            info_text="Url:{}: Running crawler {}\n{}".format(
                request.url, type(crawler), crawler_data
            ),
            stack=False,
        )

        crawler.set_settings(crawler_data)

        crawler.run()
        response = crawler.get_response()
        if response:
            response.set_crawler(crawler_data)
            if response.errors:
                for error in response.errors:
                    WebLogger.debug("Url:{}: {}".format(request.url, error))
        crawler.close()

        WebLogger.debug(
            "Url:{}: Running crawler {}\n{} DONE".format(
                request.url, type(crawler), crawler_data
            )
        )

        if response:
            return response

        self.dead = True
        WebLogger.debug("Url:{} No response from crawler".format(request.url))

        self.response = PageResponseObject(
            request.url,
            text=None,
            status_code=HTTP_STATUS_CODE_SERVER_ERROR,
            request_url=request.url,
        )
        return self.response

    def ping(self, timeout_s=5):
        url = self.url

        if url is None:
            stack_lines = traceback.format_stack()
            stack_str = "".join(stack_lines)

            WebLogger.error("Passed incorrect url {}".format(stack_str))
            return

        o = PageRequestObject(
            url=url,
            request_headers=self.headers,
            timeout_s=timeout_s,
            ping=True,
        )

        response = self.get_contents_internal(request=o)

        return response and response.is_valid()

    def get_headers_response(self, timeout_s=5):
        url = self.url

        if url is None:
            stack_lines = traceback.format_stack()
            stack_str = "".join(stack_lines)

            WebLogger.error("Passed incorrect url {}".format(stack_str))
            return

        try:
            o = PageRequestObject(
                url=url,
                headers=self.headers,
                timeout_s=timeout_s,
                ping=True,
            )

            response = self.get_contents_internal(request=o)
            if response and response.is_valid():
                return response

        except Exception as E:
            WebLogger.exc(E, "Url:{}. Header request error\n".format(url))
            return None

    def get_response_implementation(self):
        if self.response and self.response.text:
            return self.response

        if not self.user_agent or self.user_agent == "":
            self.dead = True
            return None

        if self.dead:
            return None

        if not self.is_url_valid():
            lines = traceback.format_stack()
            line_text = ""
            for line in lines:
                line_text += line

            WebLogger.error("Url:{} is invalid. Lines:{}".format(self.url, line_text))

            self.dead = True
            return None

        request = PageRequestObject(
            url=self.url,
            headers=self.headers,
            timeout_s=self.timeout_s,
        )

        self.response = self.get_contents_internal(request=request)

        return self.response

    @lazy_load_content
    def is_valid(self):
        if not self.response:
            return False

        if self.response.is_this_status_ok() or self.response.is_this_status_redirect():
            return True
        else:
            return False

    def is_url_valid(self):
        if self.url == None:
            return False

        p = UrlLocation(self.url)
        if not p.is_web_link():
            return False

        return True

    def try_decode(self, thebytes):
        try:
            return thebytes.decode("UTF-8", errors="replace")
        except Exception as e:
            pass

    def is_this_status_ok(self, status_code):
        if status_code == 0:
            return False

        return status_code >= 200 and status_code < 300


class HttpPageHandler(HandlerInterface):
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/116.0"

    def __init__(self, url=None, contents=None, settings=None, url_builder=None):
        super().__init__(
            url=url, contents=contents, settings=settings, url_builder=url_builder
        )
        self.p = None
        self.response = None
        self.settings = settings
        if not self.settings:
            self.settings = WebConfig.get_default_crawler(self.url)

        self.url_builder = url_builder

    def is_handled_by(self):
        url = self.url

        if url.startswith("https") or url.startswith("http"):
            return True
        return False

    def get_contents(self):
        """
        Obtains only contents
        """
        if self.response and self.response.get_text():
            return self.response.get_text()

        self.get_response_implementation()

        if self.response and self.response.get_text():
            return self.response.get_text()

    def get_response(self):
        """
        Obtains response, analyzes structure, etc
        """
        if self.response:
            return self.response

        self.get_response_implementation()

        self.p = self.get_page_handler()

        if self.response:
            return self.response

    def get_response_implementation(self):
        url = self.url

        dap = UrlLocation(url)

        if url.startswith("https") or url.startswith("http"):
            if not dap.is_media():
                builder = HttpRequestBuilder(url=url, settings=self.settings)
                self.response = builder.get_response()

                if not self.response:
                    return

                if not builder.is_valid():
                    return

        else:
            # Other protocols have not been yet implemented
            # there is no request, there is no response
            pass

    def get_page_handler(self):
        """
        Note: some servers might return text/html for RSS sources.
              We must manually check what kind of data it is.
              For speed - we check first what is suggested by content-type
        """
        contents = None
        if self.response and self.response.get_text():
            contents = self.response.get_text()

        if not contents:
            return

        url = self.url

        return PageFactory.get(self.response, contents)

    def get_title(self):
        if not self.p:
            return
        return self.p.get_title()

    def get_description(self):
        if not self.p:
            return
        return self.p.get_description()

    def get_language(self):
        if not self.p:
            return
        return self.p.get_language()

    def get_thumbnail(self):
        if not self.p:
            return
        return self.p.get_thumbnail()

    def get_author(self):
        if not self.p:
            return
        return self.p.get_author()

    def get_album(self):
        if not self.p:
            return
        return self.p.get_album()

    def get_tags(self):
        if not self.p:
            return
        return self.p.get_tags()

    def get_date_published(self):
        if not self.p:
            return
        return self.p.get_date_published()

    def get_canonical_url(self):
        if not self.get_response():
            self.get_response()

        if not self.p:
            return self.url
        return self.p.get_canonical_url()

    def get_properties(self):
        if not self.p:
            return

        props = self.p.get_properties()
        props["status_code"] = self.response.status_code
        return props

    def get_page_rating_vector(self):
        result = []
        if not self.p:
            return result

        """
        TODO include this somehow
        """
        if self.response:
            result.append(self.get_page_rating_status_code(self.response.status_code))

        result.extend(self.p.get_page_rating_vector())
        return result

    def get_contents_hash(self):
        if not self.p:
            return super().get_contents_hash()

        return self.p.get_contents_hash()

    def get_contents_body_hash(self):
        if not self.p:
            return super().get_contents_body_hash()

        return self.p.get_contents_body_hash()

    def get_page_rating_status_code(self, status_code):
        rating = 0
        if status_code == 200:
            rating += 10
        elif status_code >= 200 and status_code <= 300:
            rating += 5
        elif status_code != 0:
            rating += 1

        return [rating, 10]

    def get_status_code(self):
        if not self.response:
            return PageResponseObject.STATUS_CODE_UNDEF

        return self.response.status_code

    def is_valid(self):

        # not valid HTTP response
        response = self.response
        if not response or not response.is_valid():
            return False

        if self.p:
            return self.p.is_valid()

        return True

    def is_cloudflare_protected(self):
        """
        You'd probably be more successful trying to not trigger the
        bot detection in the first place rather than trying to bypass it after the fact.
        """

        if not self.p:
            return False

        return self.p.is_cloudflare_protected()

    def get_favicon(self):
        if self.p:
            if type(self.p) is HtmlPage:
                favs = self.p.get_favicons()
                if favs and len(favs) > 0:
                    return list(favs.keys())[0]

    def get_entries(self):
        if self.p:
            if type(self.p) is RssPage:
                return self.p.get_entries()
        return []

    def get_feeds(self):
        result = []
        url = self.url

        if not self.p:
            return result

        feeds = self.p.get_feeds()
        if feeds and len(feeds) > 0:
            result.extend(feeds)

        return result

    def ping(self, timeout_s=120):
        builder = HttpRequestBuilder(url=self.url, settings=self.settings)
        return builder.ping()
