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
from .cookiemanager import CookieManager

from ..entryrules import EntryRules
from utils.dateutils import DateUtils


class UrlRules(object):
    def get_default_request(url):
        page_request = WebConfig.get_default_request(url)
        # TODO close crawlwer_type?

        browser = EntryRules.get_object().get_browser(url)
        if browser:
            page_request.crawler_name = browser
            page_request.crawler_type = None

            script = WebConfig.get_script_from_name(browser)

            page_request.settings["script"] = script
            page_request.settings["remote_server"] = "http://127.0.0.1:3000"

        if page_request.timeout_s is None or page_request.timeout_s == 0:
            page_request.timeout_s = WebConfig.get_default_timeout_s()

        return page_request


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
        request = UrlRules.get_default_request(url)
        return request

    def get_request_for_request(self, request):
        """
        Fills necessary fields within request
        """
        if request.crawler_name and request.crawler_type is None:
            crawler = WebConfig.get_crawler_from_string(self.request.crawler_name)
            request.crawler_type = crawler(url=request.url, request=request)
        if request.crawler_name is None and request.crawler_type is None:
            default_request = WebConfig.get_default_request(request.url)
            request.crawler_name = default_request.crawler_name
            request.crawler_type = default_request.crawler_type

        if request.timeout_s is None or request.timeout_s == 0:
            request.timeout_s = WebConfig.get_default_timeout_s()

        cookie_manager = CookieManager()
        cookies = cookie_manager.read(request.url)
        request.cookies = cookies

        # TODO not really sure if we should use crawler interface here

        """
        interface = CrawlerInterface(request.url)
        headers = interface.get_default_headers()
        request.request_headers = headers
        """

        return request

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
