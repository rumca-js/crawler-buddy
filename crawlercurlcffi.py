"""
This script is not required, RequestsCrawler can be called directly from a project.
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

    response = None
    try:
        request = parser.get_request()

        crawler = webtools.CurlCffiCrawler(request=request)

        if parser.args.verbose:
            print("Running request:{} with RequestsCrawler".format(request))

        try:
            response = crawler.run()
        except Exception as E:
            crawler.add_error(str(E))
            response = get_response(parser.args.url, "Error in running crawler")

        try:
            crawler.close()
        except Exception as E:
            crawler.add_error(str(E))
            response = get_response(parser.args.url, "Error in closing crawler")

        if not response:
            response = crawler.response

        if not response:
            response = get_response(parser.args.url, "Missing response")

    except Exception as E:
        resonse = get_response(parser.args.url, "CurlCffi exception " + str(E))

    if response:
        print(response)
        parser.save(response)

main()
