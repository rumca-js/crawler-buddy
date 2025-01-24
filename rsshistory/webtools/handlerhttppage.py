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

    def __init__(self, url=None, options=None, page_object=None, request=None, url_builder=None):
        """
        @param url URL
        @param contents URL page contents
        @param use_selenium decides if selenium is used
        @param page_object All settings are used from page object, with page contents
        """
        self.request = request
        self.response = None
        self.timeout_s = 10

        if page_object:
            self.url = page_object.url
            self.options = page_object.options
            self.dead = page_object.dead
            self.robots_contents = page_object.robots_contents
        else:
            self.url = url
            self.options = options
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

        if not self.options:
            self.options = PageOptions()

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
        if self.options:
            request.ssl_verify = self.options.ssl_verify
        if self.options:
            request.ping = self.options.ping

        if self.options:
            mode_mapping = self.options.mode_mapping
        else:
            mode_mapping = WebConfig.get_init_crawler_config()

        request.timeout_s = self.options.get_timeout(request.timeout_s)

        if not mode_mapping or len(mode_mapping) == 0:
            self.dead = True
            WebLogger.error(
                "Url:{} Could not identify method of page capture".format(request.url)
            )
            WebLogger.error("Could not identify method of page capture")

            self.response = PageResponseObject(
                request.url,
                text=None,
                status_code=HTTP_STATUS_CODE_SERVER_ERROR,
                request_url=request.url,
            )
            return self.response

        for crawler_data in mode_mapping:
            crawler = WebConfig.get_crawler_from_mapping(request, crawler_data)
            if not crawler:
                WebLogger.debug(
                    "Cannot find crawler in WebConfig:{}".format(
                        crawler_data["crawler"]
                    )
                )
                continue

            WebLogger.debug(
                "Url:{}: Running crawler {}\n{}".format(request.url, type(crawler), crawler_data)
            )

            crawler.run()
            response = crawler.get_response()
            if response:
                response.set_crawler(crawler_data)
            crawler.close()

            WebLogger.debug(
                "Url:{}: Running crawler {}\n{} DONE".format(request.url, type(crawler), crawler_data)
            )

            if response:
                return response

        self.dead = True
        WebLogger.debug(
            "Url:{} No response from crawler".format(request.url)
        )

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

    def __init__(self, url=None, contents=None, page_options=None, url_builder=None):
        super().__init__(url=url, contents=contents, page_options=page_options, url_builder =url_builder)
        self.p = None
        self.response = None
        self.options = page_options
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
        self.get_response_once()

        if not self.options:
            WebLogger.error("No options passed")
            return

        original_mapping = self.options.mode_mapping

        if len(self.options.mode_mapping) < 2:
            return


        if (
            self.options.use_browser_promotions
            and self.is_advanced_processing_possible()
        ):
            # we warn, because if that happens too often, it is easy just to
            # define EntryRule for that domain
            WebLogger.error(
                "Url:{}. Retrying with different browser {}".format(
                    self.url,
                    self.options.mode_mapping[0],
                )
            )

            self.options.mode_mapping = self.options.mode_mapping[1:]

            self.get_response_once()

            self.options.mode_mapping = original_mapping

    def get_response_once(self):
        url = self.url

        dap = UrlLocation(url)

        if url.startswith("https") or url.startswith("http"):
            if not dap.is_media():
                builder = HttpRequestBuilder(url=url, options=self.options)
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

    def is_advanced_processing_possible(self):
        """
        If we do not have data, but we think we can do better
        """
        if self.options.mode_mapping is None:
            return False

        if not self.response:
            return True

        # content is defined, and it is not support
        content_type = self.response.get_content_type()
        if content_type and not self.response.is_content_type_supported():
            return False

        status_code = self.response.get_status_code()
        if status_code == HTTP_STATUS_CODE_CONNECTION_ERROR:
            return False

        if status_code < 200 or status_code > 404:
            return True

        # if not self.p:
        #    return True

        # if not self.p.is_valid():
        #    # if we have response, but it is invalid, we may try obtaining contents with more advanced processing
        #    return True

        text = self.response.get_text()

        if text == "" or text is None:
            return True

        return False

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
        if not self.p:
            return False

        # not valid HTTP response
        response = self.response
        if not response or not response.is_valid():
            return False

        return self.p.is_valid()

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
        # TODO ugly import
        from .handlers import RedditChannelHandler

        result = []
        url = self.url

        h = RedditChannelHandler(url)
        if h.is_handled_by():
            feeds = h.get_feeds()
            if feeds and len(feeds) > 0:
                result.extend(feeds)

        if not self.p:
            return result

        if type(self.p) is RssPage:
            # we do not add ourselve
            pass

        if type(self.p) is HtmlPage:
            feeds = self.p.get_feeds()
            if feeds and len(feeds) > 0:
                result.extend(feeds)

        return result

    def ping(self, timeout_s = 120):
        builder = HttpRequestBuilder(url=self.url, options=self.options)
        return builder.ping()
