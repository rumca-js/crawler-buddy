"""
Main Url handling class

@example
url = Url(link = "https://google.com")
response = url.get_response()

url.get_title()
"""

from urllib.parse import unquote, urlparse, parse_qs
import traceback

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
    CrawlerInterface,
)

from .webconfig import WebConfig
from .handlers import (
    YouTubeVideoHandlerJson,
    YouTubeChannelHandlerJson
)
from .requestbuilder import RequestBuilder
from utils.dateutils import DateUtils


class Url(BaseUrl):
    """
    Represents network location
    """

    def __init__(self, url=None, settings=None, request=None, url_builder=None):
        """
        Constructor. Pass url_builder, if any subsequent calls will be created using this builder.
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
        """
        Returns request for URL
        """
        request = RequestBuilder.get_default_request(url)
        return request

    def get_request_for_request(self, request):
        """
        Fills necessary fields within request
        """
        return RequestBuilder.update_request(request)

    def get_handlers(self):
        """
        Returns available handlers.
        """
        #fmt off
        return [
            YouTubeVideoHandlerJson,
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
