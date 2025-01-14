"""
Simple scraping script.
"""
import socket
import json
import traceback
import asyncio
import time
import requests

from rsshistory.webtools import (
   Url,
   RssPage,
   HtmlPage,
   fetch_url,
   fetch_all_urls,
   WebConfig,
   ScrapingClient,
)
from utils.serializers import PageDisplay, PageDisplayParser


__version__ = "0.0.1"


async def main():
    WebConfig.init()
    # we do not want to be swamped with web requests
    # WebConfig.use_print_logging()

    parser = PageDisplayParser()
    parser.parse()

    if not parser.args.url:
        parser.parser.print_help()
    else:
        display = PageDisplay(parser.args.url, parser)


if __name__ == "__main__":
    start_time = time.time()
    asyncio.run(main())
    print(f"Done in {time.time() - start_time} seconds")
