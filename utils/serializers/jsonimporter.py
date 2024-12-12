import os
import json
import traceback
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from pathlib import Path

from utils.dateutils import DateUtils
from utils.logger import get_logger

from utils.sqlmodel import (
    SqlModel,
    EntriesTable,
    EntriesTableController,
    SourcesTable,
    SourcesTableController,
    SourceOperationalData,
    SourceOperationalDataController,
)

from utils.controllers import (
    SourceDataBuilder,
    EntryDataBuilder,
    EntryWrapper,
)


class MapImporter(object):
    def __init__(self, entry_builder, source_builder, user=None, import_settings=None):
        self.entry_builder = entry_builder
        self.source_builder = source_builder
        self.user = user

        if self.user is not None:
            self.user = self.get_normal_user(user)

        self.import_settings = import_settings
        if self.import_settings is None:
            self.import_settings = {}
            self.import_settings["import_entries"] = True
            self.import_settings["import_sources"] = True
            self.import_settings["import_title"] = True
            self.import_settings["import_description"] = True
            self.import_settings["import_tags"] = True
            self.import_settings["import_comments"] = True
            self.import_settings["import_votes"] = True
            self.import_settings["import_bookmarks"] = True
            self.import_settings["import_ids"] = False

        if "import_entries" not in self.import_settings:
            self.import_settings["import_entries"] = True
        if "import_sources" not in self.import_settings:
            self.import_settings["import_sources"] = True
        if "import_title" not in self.import_settings:
            self.import_settings["import_title"] = True
        if "import_description" not in self.import_settings:
            self.import_settings["import_description"] = True
        if "import_tags" not in self.import_settings:
            self.import_settings["import_tags"] = True
        if "import_comments" not in self.import_settings:
            self.import_settings["import_comments"] = True
        if "import_votes" not in self.import_settings:
            self.import_settings["import_votes"] = True
        if "import_bookmarks" not in self.import_settings:
            self.import_settings["import_bookmarks"] = True
        if "verbose" not in self.import_settings:
            self.import_settings["verbose"] = False

    def import_from_data(self, json_data):
        if "links" in json_data:
            return self.import_from_links(json_data["links"])
        elif "sources" in json_data:
            return self.import_from_sources(json_data["sources"])
        elif "link" in json_data:
            return self.import_from_link(json_data["link"])
        elif "source" in json_data:
            return self.import_from_source(json_data["source"])
        elif len(json_data) > 0:
            return self.import_from_list(json_data)
        else:
            raise NotImplementedError()

        return False

    def import_from_list(self, json_data):
        first_item = json_data[0]
        if "link" in first_item:
            return self.import_from_links(json_data)
        elif "url" in first_item:
            return self.import_from_sources(json_data)

        return False

    def import_from_links(self, json_data):
        logger = get_logger("utils")

        logger.debug("Import from links")

        for link_data in json_data:
            try:
                self.import_from_link(link_data)
            except Exception as E:
                logger.exc(E, "Cannot import link data {}".format(link_data))

        return True

    def import_from_sources(self, json_data):
        logger = get_logger("utils")

        for source_data in json_data:
            try:
                self.import_from_source(source_data)
            except Exception as E:
                logger.exc(E, "Cannot import source data {}".format(source_data))

        return True

    def copy_props(self, entry, clean_data):
        if self.import_settings and self.import_settings["import_bookmarks"]:
            if "bookmarked" in clean_data:
                entry.bookmarked = clean_data["bookmarked"]
        if "permanent" in clean_data:
            entry.permanent = clean_data["permanent"]
        if self.import_settings and self.import_settings["import_title"]:
            if "title" in clean_data:
                entry.title = clean_data["title"]
        if self.import_settings and self.import_settings["import_description"]:
            if "description" in clean_data:
                entry.description = clean_data["description"]
        if "date_published" in clean_data:
            entry.date_published = clean_data["date_published"]
        entry.save()

    def import_from_link(self, json_data):
        """
        TODO please refactor this function. It is too big
        """
        tags = []
        if "tags" in json_data:
            tags = json_data["tags"]
        vote = None
        if "vote" in json_data:
            vote = json_data["vote"]
        comments = []
        if "comments" in json_data:
            comments = json_data["comments"]

        clean_data = self.get_clean_entry_data(json_data)

        entry = None

        if self.import_settings and self.import_settings["import_entries"]:
            # This instance can have their own settings for import, may decide what is
            # accepted and not. Let the builder deal with it
            # Logger.info("Importing link:{}".format(clean_data["link"]))

            b = self.entry_builder.import_entry(
                link_data=clean_data, source_is_auto=True
            )
            entry = b.result

        if entry:
            if self.import_settings and self.import_settings["import_bookmarks"]:
                if entry.bookmarked:
                    UserBookmarks.add(self.user, entry)
                else:
                    UserBookmarks.remove_entry(entry)

            if self.import_settings and self.import_settings["import_tags"]:
                if len(tags) > 0:
                    user = self.get_superuser()
                    for tag in tags:
                        UserTags.set_tag(entry, tag, user)

            if self.import_settings and self.import_settings["import_votes"]:
                if vote is not None:
                    UserVotes.add(self.user, entry, vote)

            if self.import_settings and self.import_settings["import_comments"]:
                if len(comments) > 0:
                    for comment in comments:
                        user = self.get_user(comment["user"])
                        data = {}

                        if entry:
                            data["entry_object"] = entry

                        if user:
                            data["user"] = user

                        data["comment"] = comment["comment"]
                        data["date_published"] = comment["date_published"]
                        data["date_edited"] = comment["date_edited"]
                        data["reply_id"] = comment["reply_id"]
                        LinkCommentDataController.add(user, entry, data)

        return True

    def import_from_source(self, json_data):
        clean_data = self.get_clean_source_data(json_data)
        clean_data["enabled"] = False

        b = self.source_builder
        b.import_source(link_data=clean_data)

        # TODO cleanup
        # else:
        #    if instance_import:
        #        source = sources[0]

        #        if source.enabled != (not clean_data["enabled"]):
        #            source.enabled = not clean_data["enabled"]

        #        if source.proxy_location != clean_data["proxy_location"]:
        #            source.proxy_location = clean_data["proxy_location"]

        #        source.save()
        return True

    def get_clean_source_data(self, data):
        return data

    def drop_entry_instance_internal_data(self, clean_data):
        if "domain_obj" in clean_data:
            del clean_data["domain_obj"]
        if "source_obj" in clean_data:
            del clean_data["domain_obj"]
        if "id" in clean_data:
            del clean_data["id"]

        return clean_data

    def drop_source_instance_internal_data(self, clean_data):
        if "dynamic_data" in clean_data:
            del clean_data["dynamic_data"]
        if "id" in clean_data:
            del clean_data["id"]

        return clean_data

    def get_clean_entry_data(self, input_data):
        clean_data = EntryWrapper.get_clean_data(input_data)
        clean_data = self.drop_entry_instance_internal_data(clean_data)

        if "date_published" in clean_data:
            clean_data["date_published"] = DateUtils.parse_datetime(
                clean_data["date_published"]
            )

        return clean_data

    def get_superuser(self):
        # TODO we do not have users in sqlalchemy
        pass

    def get_normal_user(self, username):
        # TODO we do not have users in sqlalchemy
        pass


def get_list_files(directory):
    file_list = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_list.append(os.path.join(root, file))
    return file_list


def read_file_contents(file_path):
    """
    TODO use pathlib?
    """
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


class JsonImporter(object):
    def __init__(self, conn, path=None, user=None, verbose=False):
        logger = get_logger("utils")
        logger.info("Importing from a file")
        self.user = user
        self.path = path
        self.conn = conn
        self.verbose = verbose

        if self.path is None:
            logger.error("Directory was not specified")
            return

    def import_all(self):
        logger = get_logger("utils")
        if self.path is None:
            logger.error("Directory was not specified")
            return

        path = Path(self.path)
        if path.is_file():
            self.import_from_file(self.path)
        elif path.is_dir():
            self.import_from_path(self.path)

    def import_from_path(self, path):
        files = get_list_files(path)
        for afile in files:
            if afile.endswith(".json"):
                self.import_from_file(afile)

    def import_from_file(self, afile):
        contents = read_file_contents(afile)
        if contents:
            data = json.loads(contents)

            settings = {"verbose": False}
            source_builder = SourceDataBuilder(conn=self.conn)
            entry_builder = EntryDataBuilder(conn=self.conn)
            return MapImporter(
                source_builder=source_builder,
                entry_builder=entry_builder,
                user=self.user,
                import_settings=settings,
            ).import_from_data(data)

        return False
