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

    selenium_config = WebConfig.get_seleniumfull()
    driver = WebConfig.get_crawler_from_mapping(request, selenium_config)

    driver.response_file = parser.args.output_file

    if parser.args.verbose:
        print("Running request:{} with SeleniumChromeFull".format(request))

    response = driver.run()
    if not response:
        print("No response")
        sys.exit(1)

    if parser.args.verbose:
        print("Contents")
        print(response.get_text())

    print(response)
    response_to_file(response, parser.args.output_file)
    driver.close()


main()
