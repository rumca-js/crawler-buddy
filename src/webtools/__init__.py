"""
Similar project: https://pypi.org/project/abstract-webtools/
"""

from .webconfig import WebConfig

from .url import (
    Url,
    DomainCache,
    DomainCacheInfo,
    fetch_url,
    fetch_all_urls,
)

from .handlers import (
    YouTubeChannelHandlerYdlp,
    YouTubeJsonHandler,
)

from .crawlers import (
    RequestsCrawler,
    SeleniumDriver,
    SeleniumChromeHeadless,
    SeleniumChromeFull,
    SeleniumUndetected,
    ScriptCrawler,
    StealthRequestsCrawler,
)
from .scriptcrawlerparser import (
    ScriptCrawlerParser,
)
