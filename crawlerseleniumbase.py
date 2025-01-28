"""
This script is not required, SeleniumUndetected can be called directly from a project.
 - we just show off how it can be done
 - it can be used to compare with other crawling scripts
"""

import json
import time
import argparse
import sys

from rsshistory import webtools


feature_enabled = True
try:
    from seleniumbase import SB
except Exception as E:
    feature_enabled = False


def main():
    webtools.WebConfig.init()
    webtools.WebConfig.use_print_logging()

    parser = webtools.ScriptCrawlerParser()
    parser.parse()
    if not parser.is_valid():
        sys.exit(1)
        return

    if not feature_enabled:
        print("Selenium base is not available in context")
        sys.exit(1)
        return

    request = parser.get_request()

    with SB() as sb:
        sb.open(request.url)
        page_source = sb.get_page_source()

        response = webtools.PageResponseObject(request.url)
        # TODO obtain url from SB
        # TODO obtain headers from SB
        # TODO obtain status code from SB
        response.request_url = request.url

        response.set_text(page_source)

        interface = webtools.ScriptCrawlerInterface(parser, request)
        interface.response = response
        interface.save_response()


main()
