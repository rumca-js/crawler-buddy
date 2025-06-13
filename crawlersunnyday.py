
from src import webtools

import sys


def main():
    if len(sys.argv) < 2:
        print("Usage: python scrape_cli.py <URL>")
        sys.exit(1)

    url = sys.argv[1]

    webtools.WebConfig.use_print_logging()

    parser = webtools.ScriptCrawlerParser()
    parser.parse()
    if not parser.is_valid():
        sys.exit(1)

    request = parser.get_request()
    if parser.args.verbose:
        print(f"Running request: {request} with Scrapy")

    interface = webtools.crawlers.ScriptCrawlerInterface(parser, request, __file__, "TestScriptCrawlerName")

    page_obj = webtools.PageResponseObject(request.url)
    page_obj.set_headers({})
    page_obj.status_code = 200
    page_obj.set_text("<html></html>")
    page_obj.url = request.url

    # Use interface to pass data out
    interface.response = page_obj
    interface.save_response()


if __name__ == "__main__":
    main()
