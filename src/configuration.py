"""
Provides configuration
"""
import json
import os
import logging
from pathlib import Path
from src import webtools


class Configuration(object):
    singleton = None

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
        self.data["host"] = "0.0.0.0"
        self.data["port"] = "3000"
        self.data["remote_server_ip"] = None
        self.data["max_history_records"] = 200
        self.data["max_number_of_workers"] = 5
        self.data["virtual_memory_percentage_threshold"] = 70
        self.data["scripted_crawlers"] = True
        self.data["trace"] = False
        self.data["storage_dir"] = "storage"
        self.data["history_container_db"] = False

        self.crawler_config = None

        self.read_configuration()
        self.read_crawler_config()
        self.read_version()

        if "CRAWLER_BUDDY_PORT" in os.environ:
            self.data["port"] = os.environ["CRAWLER_BUDDY_PORT"]

    def get_object():
        if Configuration.singleton is None:
            Configuration.singleton = Configuration()
        return Configuration.singleton

    def read_version(self):
        self.__version__ = "0.0.0"
        path = Path("pyproject.toml")
        text = path.read_text()
        for line in text.split("\n"):
            wh = line.find("version")
            if wh >= 0:
                self.__version__ = line[11:-1]

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
        Each crowler contains "name" and "crawler_name".
        - "crawler_name" is name of crawler class
        - "crawler_class_name" is name of browser

        There can be many crawlers with different settings.
        Crawler name needs to be unique, where crawler_class_name does not.
        """
        path = self.get_browser_file_path()
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
            name = item["crawler_name"]
            crawler_class = webtools.WebConfig.get_crawler_class_from_crawler_name(name)
            if not crawler_class:
                print(f"Could not find crawler {name}")
                continue
            if crawler_class(url="https://").is_valid():
                self.crawler_config.append(item)

        return self.crawler_config

    def get_browser_file_path(self):
        if self.data["scripted_crawlers"]:
            return Path("init_browser_setup_scripted.json")
        else:
            return Path("init_browser_setup.json")

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
        for field in json_config:
            self.data[field] = json_config[field]

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

    def get_browser(self, name=None):
        """
        Returns browser
        """
        config = self.crawler_config
        for item in config:
            if name:
                if name == item["crawler_name"]:
                    return dict(item)

    def get_crawler_class_name(self, crawler_name=None):
        """
        Returns crawler
        """
        if not crawler_name:
            return

        config = self.crawler_config
        for item in config:
            if crawler_name == item["crawler_name"]:
                return item.get("crawler_class_name")

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

    def get_memory_threshold(self):
        return self.data.get("virtual_memory_percentage_threshold")

    def set_trace(self):
        self.data["trace"] = True

    def is_trace(self):
        return self.data["trace"]

    def get_default_browser(self):
        return self.data["default_browser"]

    def get_storage_path(self):
        if self.data["storage_dir"] and self.data["storage_dir"] != "":
            return Path(self.data["storage_dir"])

    def get_remote_server(self):
        remote_server_ip = self.data["remote_server_ip"]
        port = self.data["port"]

        if remote_server_ip and remote_server_ip.strip() != "" and port:
            return f"http://{remote_server_ip}:{port}"

    def is_db_history_container(self):
        return self.data["history_container_db"]
