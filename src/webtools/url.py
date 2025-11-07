"""
Main Url handling class

@example
url = Url(link = "https://google.com")
response = url.get_response()

options.request.url
options.mode_mapping

"""

from urllib.parse import unquote, urlparse, parse_qs
from collections import OrderedDict
import urllib.robotparser
import asyncio
import base64

from webtoolkit import (
    calculate_hash,
    ContentInterface,
    DefaultContentPage,
    RssPage,
    HtmlPage,
    UrlLocation,
    WebLogger,
    URL_TYPE_RSS,
    URL_TYPE_CSS,
    URL_TYPE_JAVASCRIPT,
    URL_TYPE_HTML,
    URL_TYPE_FONT,
    URL_TYPE_UNKNOWN,
    status_code_to_text,
    response_to_json,
    request_to_json,
    HandlerInterface,
    HttpPageHandler,
)
from .webconfig import WebConfig

from .crawlers import (
    RequestsCrawler,
)

from webtoolkit import (
    BaseUrl,
    OdyseeVideoHandler,
    OdyseeChannelHandler,
    RedditUrlHandler,
    ReturnDislike,
    GitHubUrlHandler,
    HackerNewsHandler,
    InternetArchive,
    FourChanChannelHandler,
    TwitterUrlHandler,
    YouTubeVideoHandler,
    YouTubeChannelHandler,
)
from .handlers import (
    YouTubeJsonHandler,
)

from utils.dateutils import DateUtils


class Url(BaseUrl):
    """
    Encapsulates data page, and builder to make request
    """

    def __init__(self, url=None, settings=None, request=None, url_builder=None):
        """
        @param handler_class Allows to enforce desired handler to be used to process link

        There are various ways url can be specified. For simplicity we cleanup it.
        I do not like trailing slashes, no google stupid links, etc.
        """
        if not url_builder:
            url_builder = Url

        super().__init__(url=url, request=request, url_builder=url_builder)

        if not self.request.crawler_type:
            crawler = WebConfig.get_crawler_from_string(self.request.crawler_name)
            if not crawler:
                WebLogger.error(f"Could not find crawler {crawler}")
                return

            self.request.crawler_type = crawler(url=url)

    def get_request_for_url(self, url):
        return WebConfig.get_default_request(url)

    def get_request_for_request(self, request):
        default_request = WebConfig.get_default_request(request.url)
        request.crawler_name = default_request.crawler_name
        request.crawler_type = default_request.crawler_type
        return request

    def get_init_settings(self):
        return WebConfig.get_default_crawler(self.url)

    def get_init_request(self):
        return WebConfig.get_default_request(self.url)

    def get_handlers(self):
        #fmt off
        return [
            YouTubeJsonHandler,
            OdyseeVideoHandler,
            OdyseeChannelHandler,
            RedditUrlHandler,
            ReturnDislike,
            GitHubUrlHandler,
            HackerNewsHandler,
            InternetArchive,
            FourChanChannelHandler,
            TwitterUrlHandler,
            YouTubeVideoHandler,        # present here, if somebody wants to call it by name
            YouTubeChannelHandler,      # present here, if somebody wants to call it by name
            HttpPageHandler,            # default
        ]
        #fmt on
