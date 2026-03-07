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
)
from src import webtools


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
    webtools.WebConfig.init()
    webtools.WebConfig.use_print_logging()

    parser = webtools.ScriptCrawlerParser()
    parser.parse()
    if not parser.is_valid():
        sys.exit(1)
        return

    request = parser.get_request()

    try:
        driver = webtools.HttpMorphCrawler(request=request)

        if parser.args.verbose:
            print("Running request:{} with RequestsCrawler".format(request))

        response = None
        try:
            response = driver.run()
        except Exception as E:
            driver.add_error(str(E))

        try:
            driver.close()
        except Exception as E:
            driver.add_error(str(E))

        if not response:
            response = driver.response

        if response:
            print(response)
            parser.save(response)
            return
    except Exception as E:
        resonse = get_response(parser.args.url, str(E))
        print(response)
        parser.save(response)

main()
