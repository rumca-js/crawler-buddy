"""
Provides various crawling mechanisms, libraries that can crawl.
"""

from .crawlers import (
   RequestsCrawler,
   CurlCffiCrawler,
   HttpxCrawler,
   StealthRequestsCrawler,
   ScriptCrawler,
   ScriptCrawlerInterface,
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
