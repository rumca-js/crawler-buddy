import logging
import traceback
from utils.logger import get_logger


class PageSystem(object):
    """
    https://stackoverflow.com/questions/4222176/why-is-iterating-through-a-large-django-queryset-consuming-massive-amounts-of-me
    https://djangosnippets.org/snippets/1170/
    https://nextlinklabs.com/resources/insights/django-big-data-iteration

    paginator resides in django. We do not want to be dependent on django.

    @note objects need to be fetched and sliced inside of iteration, because
    otherwise queryset will fetch all of the data!

    There is also other solution - to keep, and use IDs only
    https://stackoverflow.com/questions/44206636/how-to-bulk-fetch-model-objects-from-database-handled-by-django-sqlalchemy
    """

    def __init__(self, no_entries, no_entries_per_page):
        self.no_entries = no_entries
        self.no_entries_per_page = no_entries_per_page

        if no_entries == 0:
            self.no_pages = 0
            return

        pages_float = self.no_entries / self.no_entries_per_page
        pages = int(pages_float)
        if pages_float > pages:
            pages += 1

        self.no_pages = pages

    def get_slice_limits(self, page):
        if self.no_entries == 0:
            return

        start_slice = page * self.no_entries_per_page
        end_slice = (page + 1) * self.no_entries_per_page

        if start_slice > self.no_entries:
            return

        if end_slice >= self.no_entries:
            end_slice = self.no_entries

        return [start_slice, end_slice]


class ModelCollectionConverter(object):
    def __init__(self, items):
        self.items = items

    def get_map(self):
        result = []
        for item in self.items:
            result.append(item.get_map())

        return result

    def get_map_full(self):
        result = []
        for item in self.items:
            result.append(item.get_map_full())

        return result


class ItemConverterFabric(object):
    def __init__(self, items):
        self.export_columns_all = True
        self.export_columns = []
        self.items = items

    def set_export_columns(self, export_columns):
        self.export_columns_all = False
        self.export_columns = export_columns

    def get_export_columns(self):
        if self.export_columns_all:
            keys = []
            for item in self.items:
                keys.append(item)

            self.export_columns = keys
        return self.export_columns

    def get_filtered_columns(self):
        """
        TODO - misleading. this is not only columns, but also column values
        """
        if self.export_columns_all:
            return self.items

        result = []
        for item in self.items:
            result_dict = {}
            for use_column in self.export_columns:
                if use_column in item:
                    result_dict[use_column] = item[use_column]

            result.append(result_dict)

        return result

    def export(self):
        raise NotImplemented("Not implemented")

    def from_text(self, text):
        raise NotImplemented("Not implemented")


class JsonConverter(ItemConverterFabric):
    def __init__(self, items):
        super().__init__(items)

    def export(self):
        item_data = self.get_filtered_columns()

        import json

        # if keys are not sorted, then order of keys in maps will be random
        # this can result in unnecessary export commit operations

        return json.dumps(item_data, sort_keys=True, indent=4)

    def from_text(self, text):
        import json

        return json.loads(text)


import csv
from io import StringIO


class CsvConverter(ItemConverterFabric):
    def __init__(self, items):
        super().__init__(items)
        csv.register_dialect("semi", delimiter=";", quoting=csv.QUOTE_NONE)

    def export(self):
        # TODO
        item_data = self.get_filtered_columns()

        fieldnames = self.get_export_columns()
        with StringIO() as fh:
            writer = csv.DictWriter(fh, fieldnames=fieldnames, dialect="semi")

            writer.writeheader()

            for item in item_data:
                writer.writerow(item)

            fh.seek(0)
            return fh.read()

    def from_text(self, text):
        items = []
        with StringIO(text) as fh:
            reader = csv.DictReader(fh, dialect="semi")
            for row in reader:
                items.append(row)

        return items


from string import Template


class MarkDownConverter(ItemConverterFabric):
    def __init__(self, items, item_template):
        super().__init__(items)
        self.item_template = item_template

    def export(self):
        result = ""

        items_data = self.get_filtered_columns()
        for item in items_data:
            item_data = self.use_template(item)
            result += item_data + "\n"

        return result

    def use_template(self, map_data):
        try:
            t = Template(self.item_template)
            return t.safe_substitute(map_data)
        except KeyError:
            logger = get_logger("utils")
            logger.exc(
                "Template exception {0} {1}".format(
                    self.item_template,
                    str(map_data),
                )
            )
        return ""


class MarkDownDynamicConverter(object):
    def __init__(self, items, column_order):
        self.items = items
        self.column_order = column_order

    def export(self):
        result = ""

        for item in self.items:
            column_index = 0
            for acolumn in self.column_order:
                if acolumn in item and item[acolumn] != None and item[acolumn] != []:
                    aproperty_value = item[acolumn]

                    if acolumn == "title":
                        result += " ## {}\n".format(aproperty_value)
                    elif acolumn == "link" or acolumn == "url":
                        result += " - [{}]({})\n".format(
                            aproperty_value, aproperty_value
                        )
                    else:
                        result += " - {}: {}\n".format(acolumn, aproperty_value)

                    column_index += 1

            result += "\n"

        return result


class MarkDownConverter(ItemConverterFabric):
    def __init__(self, items, item_template):
        super().__init__(items)
        self.item_template = item_template

    def export(self):
        result = ""

        items_data = self.get_filtered_columns()
        for item in items_data:
            item_data = self.use_template(item)
            result += item_data + "\n"

        return result

    def use_template(self, map_data):
        try:
            t = Template(self.item_template)
            return t.safe_substitute(map_data)
        except KeyError:
            logger = get_logger("utils")

            logger.exc(
                E,
                "Template exception {0} {1}".format(
                    self.item_template,
                    str(map_data),
                ),
            )
        return ""


class RssConverter(MarkDownConverter):
    def __init__(self, items, item_template=None):
        if item_template == None:
            super().__init__(items, self.get_template())
        else:
            super().__init__(items, item_template)

    def get_template(self):
        return '<item><title>![CDATA[$title]]</title><description>![CDATA[$description]]</description><pubDate>$date_published</pubDate><link>$link</link></item><guid isPermaLink="false">$link</guid>'


class MarkDownSourceConverter(object):
    def __init__(self, source, item_template):
        self.item_template = item_template
        self.source = source

    def export(self):
        map_data = self.source.get_map()
        return self.use_template(map_data)

    def use_template(self, map_data):
        try:
            t = Template(self.item_template)
            return t.safe_substitute(map_data)
        except KeyError:
            logger = get_logger("utils")
            logger.exc(
                E,
                "Template exception {0} {1}".format(
                    self.item_template,
                    str(map_data),
                ),
            )
        return ""
