from src import webtools

import sys
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.http import HtmlResponse
from scrapy.utils.log import configure_logging


class StatusSpider(scrapy.Spider):
    name = "status_spider"

    def __init__(self, request=None, interface=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not request or not request.url:
            raise ValueError("URL must be provided")
        self.start_urls = [request.url]
        self.request = request
        self.interface = interface

    def to_clean_headers(self, headers):
        result = {}
        for key, value in headers.items():
            if isinstance(key, bytes):
                key = key.decode("utf-8", errors="replace")
            if isinstance(value, bytes):
                value = value.decode("utf-8", errors="replace")
            if isinstance(value, list):
                str_value = ""
                for item in value:
                    str_value += item.decode("utf-8", errors="replace")
                value = str_value

            result[key] = value
        return result

    def save_response(self, response):
        page_obj = webtools.PageResponseObject(self.request.url)
        page_obj.status_code = response.status
        page_obj.url = response.url
        page_obj.request_url = self.request.url

        clean_headers = self.to_clean_headers(response.headers)
        page_obj.set_headers(clean_headers)

        self.interface.response = page_obj

        if not self.interface.is_response_valid():
            self.interface.save_response()
            return page_obj

        page_obj.set_text(response.text)

        self.interface.save_response()

        return page_obj

    def parse(self, response: HtmlResponse):
        page_obj = self.save_response(response)

        # Optionally yield for debug or live viewing
        # yield {
        #    'url': page_obj.url,
        #    'status': page_obj.status_code,
        #    'headers': page_obj.headers,
        #    'text': page_obj.text,
        # }


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

    interface = webtools.crawlers.ScriptCrawlerInterface(
        parser, request, __file__, webtools.webconfig.SCRAPY_SCRIPT
    )

    configure_logging({"LOG_LEVEL": "ERROR"})

    process = CrawlerProcess(
        settings={
            # No 'FEEDS': disables saving to JSON
        }
    )

    process.crawl(StatusSpider, request=request, interface=interface)
    process.start()


if __name__ == "__main__":
    main()
