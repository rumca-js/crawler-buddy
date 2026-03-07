"""
This script is not required, SeleniumChromeFull can be called directly from a project.
 - we just show off how it can be done
 - it can be used to compare with other crawling scripts
"""

import json
import time
import argparse
import sys

from webtoolkit import response_to_file
from src import webtools
from src.webtools import WebConfig


def get_response(link, error_text):
    response = PageResponseObject(
        url=link,
        text=None,
        status_code=HTTP_STATUS_CODE_SERVER_ERROR,
        request_url=self.request.url,
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
        request.settings["driver_executable"] = WebConfig.get_default_chromedriver_path()

        selenium_config = WebConfig.get_seleniumfull()
        driver = WebConfig.get_crawler_from_mapping(request, selenium_config)

        if parser.args.verbose:
            print("Running request:{} with SeleniumChromeFull".format(request))

        try:
            response = driver.run()
        except Exception as E:
            driver.add_error(str(E))
            response = get_response(parser.args.url, "Error in running driver")

        try:
            driver.close()
        except Exception as E:
            driver.add_error(str(E))
            response = get_response(parser.args.url, "Error in closing driver")

        if not response:
            response = driver.response

        if not response:
            response = get_response(parser.args.url, "Missing response")

    except Exception as E:
        resonse = get_response(parser.args.url, str(E))

    if response:
        print(response)
        parser.save(response)


main()
