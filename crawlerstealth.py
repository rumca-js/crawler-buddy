"""
This script is not required, SeleniumChromeFull can be called directly from a project.
 - we just show off how it can be done
 - it can be used to compare with other crawling scripts
"""

import json
import time
import argparse
import sys

from webtoolkit import (
   RequestsCrawler,
   PageResponseObject,
   HTTP_STATUS_CODE_SERVER_ERROR,
)
from src import webtools


def get_response(link, error_text):
    response = PageResponseObject(
        url=link,
        text=None,
        status_code=HTTP_STATUS_CODE_SERVER_ERROR,
        request_url=link,
    )
    response.add_error(error_text)
    return response


def main():
    webtools.WebConfig.init()
    webtools.WebConfig.use_print_logging()

    parser = webtools.ScriptCrawlerParser()
    parser.parse()
    if not parser.is_valid():
        sys.exit(1)
        return

    request = parser.get_request()

    try:
        crawler = webtools.StealthRequestsCrawler(request=request)

        if parser.args.verbose:
            print("Running request:{} with Stealth".format(request))

        response = None
        try:
            response = crawler.run()
        except Exception as E:
            crawler.add_error(str(E))

        if not response:
            print("No response")
            sys.exit(1)

        try:
            crawler.close()
        except Exception as E:
            crawler.add_error(str(E))

        if not response:
            response = crawler.response

        if response:
            parser.save(response)
        else:
            sys.exit(1)
    except Exception as E:
        resonse = get_response(parser.args.url, str(E))
        parser.save(response)


main()
