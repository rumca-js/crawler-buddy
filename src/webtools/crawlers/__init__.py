"""
Provides various crawling mechanisms, libraries that can crawl.
"""

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

from .botasaurus import BotasaurusCrawler
from .curlcffi import CurlCffiCrawler
from .httpx import HttpxCrawler
from .stealth import StealthRequestsCrawler
