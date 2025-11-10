"""
Similar project: https://pypi.org/project/abstract-webtools/
"""

from .webconfig import WebConfig

from .url import Url

from .handlers import (
    YouTubeJsonHandler,
    YouTubeChannelHandlerJson,
)

from .crawlers import (
    SeleniumDriver,
    SeleniumChromeHeadless,
    SeleniumChromeFull,
    SeleniumUndetected,
    ScriptCrawler,
    StealthRequestsCrawler,
    CurlCffiCrawler,
    HttpxCrawler,
    HttpMorphCrawler,
)
from .scriptcrawlerparser import (
    ScriptCrawlerParser,
)
