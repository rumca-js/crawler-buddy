"""
This script is not required, SeleniumUndetected can be called directly from a project.
 - we just show off how it can be done
 - it can be used to compare with other crawling scripts
"""

import json
import time
import argparse
import sys

from src import webtools
from src.webtools import WebConfig


def main():
    WebConfig.init()
    WebConfig.use_print_logging()

    parser = webtools.ScriptCrawlerParser()
    parser.parse()
    if not parser.is_valid():
        print("Script options are invalid")
        sys.exit(1)
        return

    request = parser.get_request()

    selenium_config = WebConfig.get_seleniumundetected()
    driver = WebConfig.get_crawler_from_mapping(request, selenium_config)

    driver.response_file = parser.args.output_file

    if parser.args.verbose:
        print("Running request:{} with SeleniumUndetected".format(request))

    response = driver.run()
    if not response:
        print("No response")
        sys.exit(1)

    if parser.args.verbose:
        print("Contents")
        print(response.get_text())

    print(response)
    driver.save_response()
    driver.close()


main()
