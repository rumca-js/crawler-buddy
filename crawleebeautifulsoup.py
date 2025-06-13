"""
I wanted to use crawlee directly in my project
 - I am running code in a thread (not a main thread)
 - crawlee uses asyncio, therefore I also have to use it
 - I tried creating my own loop in a thread, and on windows such system works
 - on linux raspberry it does not. Asyncio does not allow to define new loop from task
    set_wakeup_fd only works in main thread of the main interpreter

 - full asyncio http server also does not work, as only first request works, then crawlee
   complains that not all async tasks have been completed.
   No joke, asyncio http server has not completed, therefore it cannot work together

Therefore crawlee is called from a separate script. We cut off crawlee.
"""

import argparse
import sys
import os
from datetime import timedelta
import json
from src import webtools
import traceback
import shutil

os.environ["CRAWLEE_STORAGE_DIR"] = "./storage/{}".format(os.getpid())


def cleanup_storage():
    path = os.environ["CRAWLEE_STORAGE_DIR"]
    # cannot remove it yet, when program is running :(
    # shutil.rmtree(path)


crawlee_feataure_enabled = True
try:
    import asyncio

    # https://github.com/apify/crawlee-python
    # https://crawlee.dev/python/api
    from crawlee.beautifulsoup_crawler import (
        BeautifulSoupCrawler,
        BeautifulSoupCrawlingContext,
    )
    from crawlee.basic_crawler import BasicCrawler
    from crawlee.playwright_crawler import PlaywrightCrawler, PlaywrightCrawlingContext
except Exception as E:
    print(str(E))
    crawlee_feataure_enabled = False


def on_close(interface, response, status_code=0):
    interface.response = response
    interface.save_response()
    cleanup_storage()
    # crawlee complains if we kill it like this sys.exit(0)


async def main() -> None:
    webtools.WebConfig.use_print_logging()

    parser = webtools.ScriptCrawlerParser()
    parser.parse()
    if not parser.is_valid():
        sys.exit(1)
        return

    if not crawlee_feataure_enabled:
        print("Python: crawlee package is not available")
        sys.exit(1)
        return

    request = parser.get_request()
    if parser.args.verbose:
        print("Running request:{} with BeautifulSoupCrawler".format(request))

    interface = webtools.crawlers.ScriptCrawlerInterface(parser, request, __file__, webtools.webconfig.CRAWLEE_BEAUTIFUL_SCRIPT)
    response = webtools.PageResponseObject(request.url)

    if parser.args.proxy_address:
        proxy_config = ProxyConfiguration(
            proxy_urls=[parser.args.proxy_address],
        )
        crawler = BeautifulSoupCrawler(
            proxy_configuration=proxy_config,
            # Limit the crawl to max requests. Remove or increase it for crawling all links.
            max_requests_per_crawl=10,
            request_handler_timeout=timedelta(seconds=request.timeout_s),
            retry_on_blocked=False,
            max_session_rotations=2,
        )
    else:
        crawler = BeautifulSoupCrawler(
            # Limit the crawl to max requests. Remove or increase it for crawling all links.
            max_requests_per_crawl=10,
            request_handler_timeout=timedelta(seconds=request.timeout_s),
            retry_on_blocked=False,
            max_session_rotations=2,
        )

    # Define the default request handler, which will be called for every request.
    @crawler.router.default_handler
    async def request_handler(context: BeautifulSoupCrawlingContext) -> None:
        print(f"Processing {context.request.url} ...")

        try:
            # maybe we could send header information that we accept text/rss

            headers = {}
            for item in context.http_response.headers:
                headers[item] = context.http_response.headers[item]

            # result['url'] = context.request.url
            # result['loaded_url'] = context.request.loaded_url
            response.url = context.request.loaded_url
            response.request_url = request.url
            response.status_code = context.http_response.status_code
            response.set_headers(headers)

            interface.response = response

            if request.ping:
                on_close(interface, response)
                return

            if request.headers:
                on_close(interface, response)
                return

            if not interface.is_response_valid():
                print("Response is not valid")
                on_close(interface, response)
                return

            response.set_text(str(context.soup))

            print(f"Processing {context.request.url} ...DONE")
            print(response)

            on_close(interface, response)
            return

        except Exception as E:
            print(str(E))
            error_text = traceback.format_exc()
            print(error_text)

            response.status_code = webtools.HTTP_STATUS_CODE_EXCEPTION
            on_close(interface, response, 1)
            return

    try:
        # Run the crawler with the initial list of URLs.
        await crawler.run([parser.args.url])
    except Exception as E:
        print(str(E))
        error_text = traceback.format_exc()
        print(error_text)

        response.status_code = webtools.HTTP_STATUS_CODE_EXCEPTION
        on_close(interface, response, 1)
        return


if __name__ == "__main__":
    asyncio.run(main())
