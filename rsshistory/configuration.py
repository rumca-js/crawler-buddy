import json
import logging
from pathlib import Path
from rsshistory import webtools


class Configuration(object):
    def __init__(self):
        self.data = {}
        self.data["respect_robots_txt"] = False     # TODO use that
        self.data["logging_level"] = logging.INFO   # TODO use that
        self.data["ssl_verify"] = False             # TODO use that
        self.data["use_canonical_links"] = False    # TODO use that
        self.data["prefer_non_www"] = False         # TODO use that

        self.crawler_config = None
        self.read_crawler_config()

    def read_crawler_config(self):
        path = Path("init_browser_setup.json")
        if path.exists():
            print("Reading configuration from file")
            with path.open("r") as file:
                config = json.load(file)
                for index, item in enumerate(config):
                    config[index]["crawler"] = webtools.WebConfig.get_crawler_from_string(item["crawler"])

                self.crawler_config = config

                return self.crawler_config
        else:
            print("Reading configuration from webtools")
            self.crawler_config = webtools.WebConfig.get_init_crawler_config()
            return self.crawler_config

    def get_crawler_config(self):
        return self.crawler_config

    def get_crawler(self, name = None, crawler_name = None):
        config = self.crawler_config
        for item in config:
            if name:
                if name == item["name"]:
                    return item
            if crawler_name:
                if crawler_name == item["crawler"].__name__:
                    return item
