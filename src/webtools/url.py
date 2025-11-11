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
    WebLogger,
    HttpPageHandler,
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

from .webconfig import WebConfig
from .handlers import (
    YouTubeJsonHandler,
    YouTubeChannelHandlerJson
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
        if request.crawler_name and request.crawler_type is None:
            crawler = WebConfig.get_crawler_from_string(self.request.crawler_name)
            self.request.crawler_type = crawler(request.url)
        else:
            default_request = WebConfig.get_default_request(request.url)
            request.crawler_name = default_request.crawler_name
            request.crawler_type = default_request.crawler_type
        return request

    def get_init_request(self):
        request = WebConfig.get_default_request(self.url)
        request = self.get_request_for_request(request) 
        return request

    def get_handlers(self):
        #fmt off
        return [
            YouTubeJsonHandler,
            YouTubeChannelHandlerJson,
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
