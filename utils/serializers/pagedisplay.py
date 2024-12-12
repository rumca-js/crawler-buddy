import argparse

from rsshistory.webtools import (
    Url,
    RssPage,
    HtmlPage,
    WebConfig,
    HttpPageHandler,
)
from utils.services import OpenRss


class PageDisplay(object):
    def __init__(self, url, verbose=False):
        u = Url(url)
        u.get_response()

        properties = u.get_properties(full=True)

        for section in properties:
            section_name = section["name"]
            section_properties = section["data"]

            if section_name == "Contents" and not verbose:
                print("-------------")
                if len(section_properties) > 0:
                    print("There is contents")
                else:
                    print("Contents is empty")
                continue

            if section_name == "Headers" and not verbose:
                continue

            #if section_name == "Response" and not verbose:
            #    continue

            print("-------------")

            for key in section_properties:
                value = section_properties[key]
                
                if isinstance(value, str):
                    print("{}:{}".format(key, value))
                elif value is None:
                    print("{}:{}".format(key, value))
                elif isinstance(value, bool):
                    print("{}:{}".format(key, value))
                elif isinstance(value, int):
                    print("{}:{}".format(key, value))
                elif isinstance(value, dict):
                    print(key)
                    for inner_key, inner_value in value.items():
                        print("  {}:{}".format(inner_key, inner_value))
                else:
                    print(f"{key} has an unsupported type: {type(value)}")

                    print("RSS path:{}".format(Url.find_rss_url(u)))


class PageDisplayParser(object):
    """
    Headers can only be passed by input binary file
    """

    def parse(self):
        self.parser = argparse.ArgumentParser(description="Page properties")
        self.parser.add_argument(
            "--timeout", default=10, type=int, help="Timeout expressed in seconds"
        )
        self.parser.add_argument(
            "--port", type=int, default=0, help="Port, if using web scraping server"
        )
        self.parser.add_argument("--url", help="Url to fetch")
        self.parser.add_argument(
            "-v",
            "--verbose",
            action="store_true",
            help="Verbose. For example: displays full contents",
        )

        self.args = self.parser.parse_args()
