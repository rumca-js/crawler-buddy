"""
Similar project: https://pypi.org/project/abstract-webtools/
"""

from .webconfig import WebConfig

from .url import Url

from .handlers import (
    YouTubeJsonHandler,
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
)
from .scriptcrawlerparser import (
    ScriptCrawlerParser,
)
