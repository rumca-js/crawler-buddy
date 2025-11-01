"""
Provides various crawling mechanisms, libraries that can crawl.
"""

from .crawlers import (
   RequestsCrawler,
   CurlCffiCrawler,
   HttpxCrawler,
   StealthRequestsCrawler,
   BotasaurusCrawler,
)

from .seleniumbased import (
   SeleniumDriver,
   SeleniumChromeHeadless,
   SeleniumChromeFull,
   SeleniumUndetected,
   SeleniumWireFull,
   SeleniumBase,
)
from .scriptcrawler import *
from .ytdlp import *
