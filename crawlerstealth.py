"""
This script is not required, SeleniumChromeFull can be called directly from a project.
 - we just show off how it can be done
 - it can be used to compare with other crawling scripts
"""

import json
import time
import argparse
import sys

from src import webtools


def main():
    webtools.WebConfig.init()
    webtools.WebConfig.use_print_logging()

    parser = webtools.ScriptCrawlerParser()
    parser.parse()
    if not parser.is_valid():
        sys.exit(1)
        return

    request = parser.get_request()

    crawler = webtools.StealthRequestsCrawler(
        request, parser.args.output_file, parser.args.port
    )

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

    if parser.args.verbose:
        print("Contents")
        print(response.get_text())

    try:
        crawler.close()
    except Exception as E:
        crawler.add_error(str(E))

    if not response:
        response = crawler.response

    if response:
        print(response)
        parser.save(response)
    else:
        print("No response")
        sys.exit(1)


main()
