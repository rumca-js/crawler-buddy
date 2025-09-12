"""
Similar project: https://pypi.org/project/abstract-webtools/
"""

from .webtools import *
from .pages import *
from .webconfig import WebConfig
from .urllocation import UrlLocation

from .url import (
    Url,
    DomainCache,
    DomainCacheInfo,
    fetch_url,
    fetch_all_urls,
)

from .handlers import (
    HttpRequestBuilder,
    HttpPageHandler,
    YouTubeChannelHandler,
    YouTubeVideoHandler,
    YouTubeJsonHandler,
    OdyseeChannelHandler,
    OdyseeVideoHandler,
    RedditUrlHandler,
    GitHubUrlHandler,
    ReturnDislike,
    HackerNewsHandler,
    InternetArchive,
    FourChanChannelHandler,
    TwitterUrlHandler,
)

from .crawlers import (
    CrawlerInterface,
    RequestsCrawler,
    SeleniumChromeHeadless,
    SeleniumChromeFull,
    SeleniumUndetected,
    ScriptCrawler,
    StealthRequestsCrawler,
)
from .remoteserver import RemoteServer
from .crawlerscript import (
    ScriptCrawlerParser,
)

from .feedclient import FeedClient, FeedClientParser

from .contentmoderation import (
    UrlPropertyValidator,
    UrlPropertyValidator,
    UrlAgeModerator,
)
