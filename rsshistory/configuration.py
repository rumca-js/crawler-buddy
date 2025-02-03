import json
import logging
from pathlib import Path
from rsshistory import webtools


class Configuration(object):
    def __init__(self):
        self.data = {}
        self.data["respect_robots_txt"] = False  # TODO use that
        self.data["logging_level"] = logging.INFO  # TODO use that
        self.data["ssl_verify"] = False  # TODO use that
        self.data["use_canonical_links"] = False  # TODO use that
        self.data["prefer_non_www"] = False  # TODO use that
        self.data["debug"] = True  # TODO use that

        self.crawler_config = None

        self.read_configuration()
        self.read_crawler_config()

    def is_set(self, name):
        if name in self.data:
            return self.data[name]

        return False

    def read_crawler_config(self):
        path = Path("init_browser_setup.json")
        if path.exists():
            print("Reading crawler config from file")
            with path.open("r") as file:
                config = json.load(file)
                for index, item in enumerate(config):
                    config[index]["crawler"] = (
                        webtools.WebConfig.get_crawler_from_string(item["crawler"])
                    )

                self.crawler_config = config

                return self.crawler_config
        else:
            print("Reading crawler config from webtools")
            self.crawler_config = webtools.WebConfig.get_init_crawler_config()
            return self.crawler_config

    def read_configuration(self):
        path = Path("configuration.json")
        if path.exists():
            print("Reading configuration:{}".format(str(path)))
            with path.open("r") as file:
                json_config = json.load(file)

                if "debug" in json_config:
                    self.data["debug"] = json_config["debug"]
                if "respect_robots_txt" in json_config:
                    self.data["respect_robots_txt"] = json_config["respect_robots_txt"]
                if "ssl_verify" in json_config:
                    self.data["ssl_verify"] = json_config["ssl_verify"]
                if "prefer_non_www" in json_config:
                    self.data["prefer_non_www"] = json_config["prefer_non_www"]
                if "use_canonical_links" in json_config:
                    self.data["use_canonical_links"] = json_config[
                        "use_canonical_links"
                    ]
                if "allowed_ids" in json_config:
                    self.data["allowed_ids"] = json_config["allowed_ids"]

    def get_crawler_config(self):
        return self.crawler_config

    def get_crawler(self, name=None, crawler_name=None):
        config = self.crawler_config
        for item in config:
            if name:
                if name == item["name"]:
                    return dict(item)
            if crawler_name:
                if crawler_name == item["crawler"].__name__:
                    return dict(item)

    def is_allowed(self, id):
        if "allowed_ids" in self.data:
            if len(self.data["allowed_ids"]) == 0:
                return True

            if id == "" or id is None:
                return False

            if id in self.data["allowed_ids"]:
                return True
            return False
        return True
