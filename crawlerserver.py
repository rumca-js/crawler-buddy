"""
This script is not required, driver can be called directly from a project.
 - we just show off how it can be done
 - it can be used to compare with other crawling scripts
"""

import json
import time
import argparse
import sys

from src import webtools


def main():
    webtools.WebConfig.use_print_logging()

    parser = webtools.ScriptCrawlerParser()
    parser.parse()
    if not parser.is_valid():
        sys.exit(1)
        return

    if not parser.args.output_file:
        print("Please specify output directory")
        sys.exit(1)
        return

    request = parser.get_request()

    driver = webtools.ServerCrawler(
        request,
        response_file=parser.args.output_file,
        response_port=parser.args.port,
        script="poetry run python crawlerrequests.py",
    )

    if parser.args.verbose:
        print("Running request:{} with ServerCrawler".format(request))

    if not driver.run():
        print("Cannot start driver")
        sys.exit(1)
        return

    driver.save_response()
    driver.close()


main()
