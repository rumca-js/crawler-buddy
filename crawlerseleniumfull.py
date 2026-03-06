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


def main():
    WebConfig.init()
    WebConfig.use_print_logging()

    parser = webtools.ScriptCrawlerParser()
    parser.parse()
    if not parser.is_valid():
        sys.exit(1)
        return

    request = parser.get_request()
    request.settings["driver_executable"] = WebConfig.get_default_chromedriver_path()

    selenium_config = WebConfig.get_seleniumfull()
    driver = WebConfig.get_crawler_from_mapping(request, selenium_config)

    if parser.args.verbose:
        print("Running request:{} with SeleniumChromeFull".format(request))

    response = None
    try:
        response = driver.run()
    except Exception as E:
        driver.add_error(str(E))

    if not response:
        print("No response")
        sys.exit(1)

    try:
        driver.close()
    except Exception as E:
        driver.add_error(str(E))

    if not response:
        response = driver.response

    if response:
        print(response)
        parser.save(response)
    else:
        print("No response")
        sys.exit(1)


main()
