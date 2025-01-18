"""
TODO:
     - we want to find only entries within mintes of last query
"""
from datetime import datetime


class CrawlHistory(object):
    def __init__(self, size=200, time_cache_m = 10):
        """
        @param time_cache_m Time Cache in minutes
        """
        self.size = size
        self.time_cache_m = time_cache_m
        self.container = []
        self.index = 0

    def set_time_cache(self, time_cache_m):
        self.time_cache_m = time_cache_m

    def set_size(self, size):
        self.size = size

    def get_history_size(self):
        return len(self.container)

    def add(self, things):
        to_add = [datetime.now(), self.index, things]

        if len(self.container) > self.size:
            self.container.pop(0)

        self.container.append(to_add)

        self.index += 1

    def get_history(self):
        return self.container

    def find(self, index = None, url = None, crawler_name= None, crawler = None):
        """
        return index
        """
        last_found = None

        for datetime, index, things in reversed(self.container):
            container_url = things[0]
            all_properties = things[1]

            if url == container_url and all_properties:
                response = CrawlHistory.read_properties_section("Response", all_properties)

                if crawler_name and response and "crawler_data" in response and "name" in response["crawler_data"]:
                    if crawler_name != response["crawler_data"]["name"]:
                        continue

                if crawler and response and "crawler_data" in response and "crawler" in response["crawler_data"]:
                    if crawler!= response["crawler_data"]["crawler"]:
                        continue

                return all_properties

    def read_properties_section(section_name, all_properties):
        for properties in all_properties:
            if section_name == properties["name"]:
                return properties["data"]
