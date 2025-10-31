from webtoolkit import PageResponseObject, response_to_file
from src import webtools
from src.webtools import Url

import sys


def main():
    if len(sys.argv) < 2:
        print("Usage: python --url <URL>")
        sys.exit(1)

    url = sys.argv[1]

    webtools.WebConfig.use_print_logging()

    parser = webtools.ScriptCrawlerParser()
    parser.parse()
    if not parser.is_valid():
        sys.exit(1)

    request = parser.get_request()
    if parser.args.verbose:
        print(f"Running request: {request}")

    u = Url(url=parser.args.url)
    response = u.get_response()

    # Use interface to pass data out
    response_to_file(response, parser.args.output_file)
    print(response)


if __name__ == "__main__":
    main()
