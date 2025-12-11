"""
Provides configuration
"""
import json
import logging
from pathlib import Path
from src import webtools


class Configuration(object):
    def __init__(self):
        """
        Constructor.
        """
        self.data = {}
        self.data["respect_robots_txt"] = False
        self.data["logging_level"] = logging.INFO  # TODO use that
        self.data["ssl_verify"] = False
        self.data["use_canonical_links"] = False  # TODO use that
        self.data["prefer_non_www"] = False  # TODO use that
        self.data["debug"] = True  # TODO use that
        self.data["default_crawler"] = None
        self.data["host"] = "127.0.0.1"
        self.data["port"] = "3000"
        self.data["max_history_records"] = 200
        self.data["max_number_of_workers"] = 5

        self.crawler_config = None

        self.read_configuration()
        self.read_crawler_config()

        # increment major version digit for releases, or link name changes
        # increment minor version digit for JSON data changes
        # increment last digit for small changes
        self.__version__ = "6.0.60"

    def is_set(self, name) -> bool:
        """
        Returns information if 'name' setting was defined
        """
        if name in self.data and self.data[name]:
            return True

        return False

    def get(self, name):
        """
        Returns name setting
        """
        if name in self.data:
            return self.data[name]

    def read_crawler_config(self):
        """
        Reads crawler config
        """
        path = Path("init_browser_setup.json")
        if path.exists():
            print(f"Reading crawler config from file {path}")
            with path.open("r") as file:
                config = json.load(file)
                crawler_config = config
        else:
            print("Using default crawler config")
            crawler_config = webtools.WebConfig.get_init_crawler_config()

        self.crawler_config = []

        for item in crawler_config:
            name = item["name"]
            crawler = webtools.WebConfig.get_crawler_from_string(name)
            if not crawler:
                print(f"Could not find crawler {name}")
                continue
            if crawler("https://").is_valid():
                self.crawler_config.append(item)

        return self.crawler_config

    def read_configuration(self):
        """
        Reads configuration file
        """
        path = Path("configuration.json")
        if path.exists():
            print("Reading configuration:{}".format(str(path)))
            with path.open("r") as file:
                json_config = json.load(file)
                self.read_json_config(json_config)

    def read_json_config(self, json_config):
        """
        Reads particular options from JSON to internal structures
        """
        self.read_json_config_field(json_config, "debug")
        self.read_json_config_field(json_config, "respect_robots_txt")
        self.read_json_config_field(json_config, "ssl_verify")
        self.read_json_config_field(json_config, "prefer_non_www")
        self.read_json_config_field(json_config, "use_canonical_links")
        self.read_json_config_field(json_config, "allowed_ids")
        self.read_json_config_field(json_config, "default_crawler")
        self.read_json_config_field(json_config, "bytes_limit")
        self.read_json_config_field(json_config, "host")
        self.read_json_config_field(json_config, "port")
        self.read_json_config_field(json_config, "max_number_of_workers")
        self.read_json_config_field(json_config, "max_history_records")

    def read_json_config_field(self, json_config, field):
        """
        Reads JSON structure field to internal placeholder
        """
        if field in json_config:
            self.data[field] = json_config[field]

    def get_crawler_config(self):
        """
        Returns crawler configuration
        """
        return self.crawler_config

    def get_crawler(self, name=None):
        """
        Returns crawler
        """
        config = self.crawler_config
        for item in config:
            if name:
                if name == item["name"]:
                    return dict(item)

    def is_allowed(self, id) -> bool:
        """
        Returns information if 'id' token is allowed
        """
        if "allowed_ids" in self.data:
            if len(self.data["allowed_ids"]) == 0:
                return True

            if id == "" or id is None:
                return False

            if id in self.data["allowed_ids"]:
                return True
            return False
        return True

    def get_max_workers(self):
        return self.data.get("max_number_of_workers")
