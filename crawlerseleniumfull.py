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
   PageResponseObject,
   HTTP_STATUS_CODE_SERVER_ERROR,
)

from src import webtools
from src.webtools import WebConfig, SeleniumChromeFull


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
    WebConfig.init()
    WebConfig.use_print_logging()

    parser = webtools.ScriptCrawlerParser()
    parser.parse()
    if not parser.is_valid():
        sys.exit(1)
        return

    response = None
    try:
        request = parser.get_request()
        request.settings["driver_executable"] = str(WebConfig.get_default_chromedriver_path())

        selenium_config = WebConfig.get_seleniumfull()
        crawler = SeleniumChromeFull(request=request)

        if parser.args.verbose:
            print("Running request:{} with SeleniumChromeFull".format(request))

        try:
            response = crawler.run()
        except Exception as E:
            crawler.add_error(str(E))

        try:
            crawler.close()
        except Exception as E:
            crawler.add_error(str(E))
            response = get_response(parser.args.url, "Error in closing driver")

        if response is None:
            response = crawler.get_response()

        if response is None:
            response = get_response(parser.args.url, "Missing response")

    except Exception as E:
        resonse = get_response(parser.args.url, str(E))

    if response is not None:
        parser.save(response)


main()
