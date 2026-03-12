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
   response_to_file,
   HTTP_STATUS_CODE_SERVER_ERROR,
)

from src import webtools
from src.webtools import WebConfig


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
        crawler = WebConfig.get_crawler_from_mapping(request, selenium_config)

        if parser.args.verbose:
            print("Running request:{} with SeleniumChromeFull".format(request))

        if not crawler:
            response = get_response(parser.args.url, "Cannot obtain crawler")

        if crawler:
            try:
                response = crawler.run()
            except Exception as E:
                crawler.add_error(str(E))
                response = get_response(parser.args.url, "Error in running driver")

            try:
                crawler.close()
            except Exception as E:
                crawler.add_error(str(E))
                response = get_response(parser.args.url, "Error in closing driver")

            if not response:
                response = crawler.get_response()

            if not response:
                response = get_response(parser.args.url, "Missing response")

    except Exception as E:
        resonse = get_response(parser.args.url, str(E))

    if response:
        print(response)
        parser.save(response)


main()
