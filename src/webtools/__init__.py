"""
Similar project: https://pypi.org/project/abstract-webtools/
"""

from .webconfig import WebConfig

from .url import Url

from .handlers import (
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
