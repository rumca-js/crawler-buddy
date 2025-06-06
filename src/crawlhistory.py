"""
TODO:
     - we want to find only entries within mintes of last query
"""

from datetime import datetime, timedelta


class CrawlHistory(object):
    def __init__(self, size=200, time_cache_m=10):
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

    def find(self, index=None, url=None, crawler_name=None, crawler=None):
        """
        return index
        """
        last_found = None

        for timestamp, inner_index, things in reversed(self.container):
            container_url = things[0]
            all_properties = things[1]

            if (datetime.now() - timestamp) > timedelta(minutes=10):
                continue

            if url is not None and url != container_url:
                continue

            if index is not None and index != inner_index:
                continue

            settings = CrawlHistory.read_properties_section("Settings", all_properties)

            if (
                crawler_name is not None
                and settings
                and "name" in settings
                and settings["name"]
            ):
                if crawler_name != settings["name"]:
                    continue

            if (
                crawler is not None
                and settings
                and "crawler" in settings
                and settings["crawler"]
            ):
                if crawler != settings["crawler"]:
                    continue

            return inner_index, timestamp, all_properties

    def remove(self, index):
        """
        return index
        """
        last_found = False

        result = []

        for timestamp, inner_index, things in self.container:
            if index != inner_index:
                result.append([timestamp, inner_index, things])
            else:
                last_found = True

        self.container = result

        return last_found

    def read_properties_section(section_name, all_properties):
        for properties in all_properties:
            if "name" in properties:
                if section_name == properties["name"]:
                    return properties["data"]
