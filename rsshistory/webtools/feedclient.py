"""
This is example script about how to use this project as a simple RSS reader
"""

import argparse
import sys
import asyncio
from pathlib import Path
import shutil
from sqlalchemy import desc, asc

from utils.sqlmodel import (
    SqlModel,
    EntriesTable,
    EntriesTableController,
    SourcesTable,
    SourcesTableController,
    SourceOperationalData,
    SourceOperationalDataController,
    ReadMarkers,
)
from datetime import timedelta, datetime, timezone

from .webtools import PageOptions
from .webconfig import WebConfig
from .pages import RssPage
from .url import Url
from .handlerhttppage import HttpPageHandler

from utils.dateutils import DateUtils
from utils.serializers import HtmlExporter, JsonImporter
from utils.controllers import GenericEntryController
from utils.alchemysearch import AlchemySearch, AlchemyRowHandler


__version__ = "0.0.4"


def print_entry(row):
    link = row.link
    date_published = row.date_published

    ec = GenericEntryController(row, console=True)
    title = ec.get_title(True)

    print("-------------------")
    print(title)
    print(date_published)
    print(link)
    print()


def print_source(source):
    print("-------------------")
    print("[{}] Title:{} Enabled:{}".format(source.id, source.title, source.enabled))
    print("Url:{}".format(source.url))
    print()


def read_source(db, source):
    result = []

    source_url = source.url
    source_title = source.title
    source_id = source.id

    url = Url(url=source_url)
    handler = url.get_handler()
    response = url.get_response()

    if not handler:
        print("Cannot obtain handler for:{}".format(source_url))
        return

    if response:
        entries = handler.get_entries()

        if not entries:
            print("Cannot obtain entries for:{}".format(source_url))
            return result

        for item in entries:
            item["source"] = source_url
            item["source_title"] = source_title
            item["source_obj__id"] = source_id
            result.append(item)

    print("\rRead:{}".format(source_url), end="")

    return result


class OutputWriter(object):
    def __init__(self, db, entries, date_limit=None):
        self.db = db
        self.entries = entries
        self.date_limit = date_limit

    def write(self):
        for entry in self.entries:
            thumbnail = entry.thumbnail
            title = entry.title
            link = entry.link
            description = entry.description
            date_published = entry.date_published

            if self.date_limit and date_published > self.date_limit:
                print_entry(entry)
            elif not self.date_limit:
                print_entry(entry)

        print(self.date_limit)


def fetch(db, parser, day_limit):
    """
    fetch time is used to not spam servers every time you refresh anything
    """
    Session = db.get_session()
    with Session() as session:
        q = session.query(EntriesTable)
        print("")

    sources = []
    with Session() as session:
        sources = session.query(SourcesTable).filter(SourcesTable.enabled == True).all()

    for source in sources:
        date_now = DateUtils.get_datetime_now_utc()
        date_now = date_now.replace(tzinfo=None)

        if not parser.args.force:
            operational_data = SourceOperationalDataController(db, session)
            if not operational_data.is_fetch_possible(source, date_now, 60 * 10):
                if parser.args.verbose:
                    print("Source {} does not require fetch yet".format(source.title))
                continue

        date_now = DateUtils.get_datetime_now_utc()
        date_now = date_now.replace(tzinfo=None)
        op_con = SourceOperationalDataController(db)
        op_con.set_fetched(source, date_now)

        print("\rReading {}".format(source.url), end="")
        source_entries = read_source(db, source)

        for entry in source_entries:
            now = datetime.now(timezone.utc)
            limit = now - timedelta(days=day_limit)

            entires_num = 0
            with Session() as session:
                entires_num = (
                    session.query(EntriesTable)
                    .filter(EntriesTable.link == entry["link"])
                    .count()
                )

            if entry["date_published"] > limit and entires_num == 0:
                ec = EntriesTableController(db)
                ec.add_entry(entry)

        with Session() as session:
            q = session.query(EntriesTable)
            print("Number of entries:{}".format(q.count()))


async def fetch_async(db, parser, day_limit):
    """
    Async version is faster than sequentially asking all sites.
    fetch time is used to not spam servers every time you refresh anything
    """
    print("")

    sources = []
    Session = db.get_session()
    with Session() as session:
        sources = session.query(SourcesTable).filter(SourcesTable.enabled == True).all()

    threads = []
    sources_fetched = []
    for source in sources:
        date_now = DateUtils.get_datetime_now_utc()
        date_now = date_now.replace(tzinfo=None)

        if not parser.args.force:
            operational_data = SourceOperationalDataController(db)
            if not operational_data.is_fetch_possible(source, date_now, 60 * 10):
                if parser.args.verbose:
                    print("Source {} does not require fetch yet".format(source.title))
                continue

        print("\rReading:{}".format(source.title), end="")

        thread = asyncio.to_thread(read_source, db, source)
        threads.append(thread)
        sources_fetched.append(source)

    results = await asyncio.gather(*threads)

    # outside of threads

    for source in sources_fetched:
        date_now = DateUtils.get_datetime_now_utc()
        date_now = date_now.replace(tzinfo=None)

        op_con = SourceOperationalDataController(db)
        op_con.set_fetched(source, date_now)

    total_added_entries = 0

    for result in results:
        for entry in result:
            now = datetime.now(timezone.utc)
            limit = now - timedelta(days=day_limit)

            entires_num = 0
            with Session() as session:
                entires_num = (
                    session.query(EntriesTable)
                    .filter(EntriesTable.link == entry["link"])
                    .count()
                )

            if entry["date_published"] > limit and entires_num == 0:
                ec = EntriesTableController(db)
                ec.add_entry(entry)
                total_added_entries += 1

    print(f"\nAdded {total_added_entries}")

    with Session() as session:
        q = session.query(EntriesTable)
        print("Number of entries:{}".format(q.count()))


class FeedClientParser(object):
    """
    Headers can only be passed by input binary file
    """

    def parse(self):
        self.parser = argparse.ArgumentParser(
            description="""RSS feed program. """,
        )
        self.parser.add_argument(
            "--timeout", default=10, type=int, help="Timeout expressed in seconds"
        )
        self.parser.add_argument(
            "--port", type=int, default=0, help="Port, if using web scraping server"
        )
        self.parser.add_argument("-o", "--output-dir", help="HTML output directory")
        self.parser.add_argument("--add", help="Adds entry with the specified URL")
        self.parser.add_argument(
            "--bookmark", action="store_true", help="bookmarks entry"
        )
        self.parser.add_argument(
            "--unbookmark", action="store_true", help="unbookmarks entry"
        )
        self.parser.add_argument(
            "-m", "--mark-read", action="store_true", help="Marks entries as read"
        )
        self.parser.add_argument("--entry", help="Select entry by ID")
        self.parser.add_argument("--source", help="Select source by ID")
        self.parser.add_argument(
            "-r",
            "--refresh-on-start",
            action="store_true",
            help="Refreshes links, fetches on start",
        )
        self.parser.add_argument("--force", action="store_true", help="Force refresh")
        self.parser.add_argument(
            "--stats", action="store_true", help="Show table stats"
        )
        self.parser.add_argument(
            "--cleanup", action="store_true", help="Remove unreferenced items"
        )
        self.parser.add_argument("--follow", help="Follows specific source")
        self.parser.add_argument("--unfollow", help="Unfollows specific source")
        self.parser.add_argument(
            "--unfollow-all", action="store_true", help="Unfollows all sources"
        )
        self.parser.add_argument("--enable", help="Enables specific source")
        self.parser.add_argument("--disable", help="Disables specific source")
        self.parser.add_argument(
            "--enable-all", action="store_true", help="Enables all sources"
        )
        self.parser.add_argument(
            "--disable-all", action="store_true", help="Disables all sources"
        )
        self.parser.add_argument(
            "--list-bookmarks", action="store_true", help="Prints bookmarks to stdout"
        )
        self.parser.add_argument(
            "--list-entries", action="store_true", help="Prints data to stdout"
        )
        self.parser.add_argument(
            "--list-sources", action="store_true", help="Lists sources"
        )
        self.parser.add_argument(
            "--init-sources", action="store_true", help="Initializes sources"
        )
        self.parser.add_argument(
            "--page-details", help="Shows page details for specified URL"
        )
        self.parser.add_argument(
            "--search", help="""Search entries. Example: --search "title=Elon" """
        )
        self.parser.add_argument("-v", "--verbose", action="store_true", help="Verbose")
        self.parser.add_argument(
            "--db", default="feedclient.db", help="SQLite database file name"
        )

        # TODO implement
        # --since "2024-01-01 12:03

        self.args = self.parser.parse_args()


class SearchResultHandler(AlchemyRowHandler):
    def __init__(self):
        super().__init__()

    def handle_row(self, row):
        print_entry(row)


def get_entries(db, source_id=None, ascending=True):
    Session = db.get_session()

    with Session() as session:
        query = session.query(EntriesTable)

        if source_id:
            query = query.filter(EntriesTable.source_obj__id == source_id)

        if ascending:
            query = query.order_by(asc(EntriesTable.date_published))
        else:
            query = query.order_by(desc(EntriesTable.date_published))

        return query.all()


class FeedClient(object):
    def __init__(self, day_limit=7, engine=None, parser=None):
        self.day_limit = day_limit
        self.engine = engine

        if parser:
            self.parser = parser

    def run(self):
        database_file = self.parser.args.db

        db = SqlModel(database_file=database_file, engine=self.engine)

        if self.parser.args.init_sources:
            importer = JsonImporter(db, "init_sources.json")
            importer.import_all()

        if self.parser.args.cleanup:
            db.entries_table.truncate()

        if self.parser.args.add:
            self.add_entry(db, self.parser.args.add)

        if self.parser.args.bookmark:
            self.make_bookmarked(db, self.parser.args.entry)

        if self.parser.args.unbookmark:
            self.make_not_bookmarked(db, self.parser.args.entry)

        if self.parser.args.follow:
            if not self.follow_url(db, self.parser.args.follow):
                print("Cannot follow {}".format(self.parser.args.follow))

        if self.parser.args.unfollow:
            self.unfollow_url(db, self.parser.args.unfollow)

        if self.parser.args.unfollow_all:
            self.unfollow_all(db)

        if self.parser.args.enable:
            self.enable_source(db, self.parser.args.enable)

        if self.parser.args.disable:
            self.disable_source(db, self.parser.args.disable)

        if self.parser.args.enable_all:
            self.enable_all_sources(db)

        if self.parser.args.disable_all:
            self.disable_all_sources(db)

        if self.parser.args.mark_read:
            self.mark_read(db)

        # one of the below needs to be true
        if self.parser.args.refresh_on_start:
            c = EntriesTableController(db)
            c.remove(self.day_limit)

            # fetch(db, self.parser, self.day_limit)
            asyncio.run(fetch_async(db, self.parser, self.day_limit))
            date_now = DateUtils.get_datetime_now_utc()
            print("Current time:{}".format(date_now))

        if self.parser.args.list_sources:
            self.list_sources(db)

        if self.parser.args.list_bookmarks:
            self.list_bookmarks(db)

        if self.parser.args.stats:
            self.show_stats(db)

        if self.parser.args.output_dir:
            directory = Path(self.parser.args.output_dir)
            if not directory.exists():
                directory.mkdir(parents=True, exist_ok=True)
            else:
                shutil.rmtree(str(directory))
                directory.mkdir(parents=True, exist_ok=True)

            entries = get_entries(db, self.parser.args.source, ascending=False)

            verbose = False
            if self.parser.args.verbose:
                verbose = True

            w = HtmlExporter(directory, entries, verbose=verbose)
            w.write()

        if self.parser.args.search:
            s = AlchemySearch(
                db, self.parser.args.search, row_handler=SearchResultHandler()
            )
            s.search()

        if self.parser.args.page_details:
            from utils.serializers import PageDisplay

            PageDisplay(self.parser.args.page_details, verbose=self.parser.args.verbose)

        if self.parser.args.list_entries:
            entries = get_entries(db, self.parser.args.source, ascending=True)

            date_limit = None
            Session = db.get_session()
            with Session() as session:
                read_marker = (
                    session.query(ReadMarkers)
                    .filter(ReadMarkers.source_object == None)
                    .first()
                )
                if read_marker:
                    date_limit = read_marker.read_date

            w = OutputWriter(db, entries, date_limit)
            w.write()

    def enable_all_sources(self, db):
        Session = db.get_session()

        with Session() as session:
            sources = session.query(SourcesTable).all()
            for source in sources:
                source.enabled = True
                session.commit()

            print("Enabled all sources")

            return True

        return False

    def disable_all_sources(self, db):
        Session = db.get_session()

        with Session() as session:
            sources = session.query(SourcesTable).all()
            for source in sources:
                source.enabled = False
                session.commit()

            print("Disabled all sources")

            return True

        return False

    def enable_source(self, db, source_id):
        Session = db.get_session()

        try:
            source_id_int = int(source_id)
        except ValueError:
            print("Cannot find such source:{}".format(source_id))
            return False

        with Session() as session:
            source = (
                session.query(SourcesTable)
                .filter(SourcesTable.id == source_id_int)
                .first()
            )
            if source:
                if source.enabled == True:
                    print("Source is already enabled")
                else:
                    source.enabled = True
                    session.commit()
                    return True
            else:
                print("Source does not exist")

        return False

    def disable_source(self, db, source_id):
        Session = db.get_session()

        try:
            source_id_int = int(source_id)
        except ValueError:
            print("Cannot find such source:{}".format(source_id))
            return False

        with Session() as session:
            source = (
                session.query(SourcesTable)
                .filter(SourcesTable.id == source_id_int)
                .first()
            )

            if source:
                if source.enabled == False:
                    print("Source is already disabled")
                else:
                    source.enabled = False
                    session.commit()
                    return True
            else:
                print("Source does not exist")

        return False

    def mark_read(self, db):
        Session = db.get_session()
        with Session() as session:
            ReadMarkers.set(session)

        print("Marked as read")

    def follow_url(self, db, page_url):
        def is_source(db, page_url):
            Session = db.get_session()

            with Session() as session:
                count = (
                    session.query(SourcesTable)
                    .filter(SourcesTable.url == page_url)
                    .count()
                )
                if count != 0:
                    return True

        source = {}

        if is_source(db, page_url):
            print("Such source is already added")
            return False

        u = Url(page_url)
        u.get_response()

        url = Url.find_rss_url(u)
        if not url:
            print("That does not seem to be a correct RSS source:{}".format(page_url))
            return

        response = url.get_response()
        title = url.get_title()

        if not title:
            title = input("Specify title of URL")

        source["url"] = url.url
        source["title"] = title

        if is_source(db, url.url):
            print("Such source is already added")

        Session = db.get_session()
        with Session() as session:
            session.add(SourcesTable(url=url.url, title=title))
            session.commit()

        print("You started following {}/{}".format(url.url, title))

        return True

    def unfollow_url(self, db, url):
        Session = db.get_session()

        sources = []
        with Session() as session:
            sources = session.query(SourcesTable).filter(SourcesTable.url == url).all()

            if len(sources) == 0:
                return False

            for source in sources:
                session.delete(source)

            session.commit()

        print("You stopped following {}".format(url))

        return True

    def unfollow_all(self, db):
        Session = db.get_session()

        sources = []
        with Session() as session:
            sources = session.query(SourcesTable).all()
            for source in sources:
                session.delete(source)

            session.commit()

        print("Unfollowed all sources")
        return True

    def list_sources(self, db):
        Session = db.get_session()
        with Session() as session:
            sources = session.query(SourcesTable).all()

            for source in sources:
                print_source(source)

    def list_bookmarks(self, db):
        Session = db.get_session()

        with Session() as session:
            query = session.query(EntriesTable)

            query = query.filter(EntriesTable.bookmarked == True)
            query = query.order_by(desc(EntriesTable.date_published))

            entries = query.all()

            for entry in entries:
                print_entry(entry)

    def show_stats(self, db):
        Session = db.get_session()

        with Session() as session:
            q = session.query(EntriesTable)
            count_entries = q.count()

            q = session.query(SourcesTable)
            count_sources = q.count()

            print(f"Entires:{count_entries}")
            print(f"Sources:{count_sources}")

    def add_entry(self, db, url):
        u = Url(url=url)
        response = u.get_response()
        if not response or not response.is_valid():
            print("Cannot obtain link properties")

        properties = u.get_properties()
        if "link" not in properties or properties["link"] is None:
            print("Cannot obtain link properties")
            return False

        if "title" not in properties or properties["title"] is None:
            print("Cannot obtain link properties")
            return False

        Session = db.get_session()
        entry = EntriesTable(**properties)

        with Session() as session:
            if (
                session.query(EntriesTable).filter(EntriesTable.link == url).count()
                != 0
            ):
                print("Link is already present in the database")
                return False

            session.add(entry)
            session.commit()

        return True

    def make_bookmarked(self, db, entry_id):
        try:
            entry_id_int = int(entry_id)
        except ValueError:
            print("Cannot bookmark")
            return False

        Session = db.get_session()
        with Session() as session:
            entries = session.query(EntriesTable).filter(
                EntriesTable.id == entry_id_int
            )

            if entries.count() == 0:
                print("Entry {} is not present in the database".format(entry_id))
                return False

            entry = entries.first()
            entry.bookmarked = True

            session.commit()
            print("Bookmarked")

        return True

    def make_not_bookmarked(self, db, entry_id):
        try:
            entry_id_int = int(entry_id)
        except ValueError:
            print("Cannot bookmark")
            return False

        Session = db.get_session()
        with Session() as session:
            entries = session.query(EntriesTable).filter(
                EntriesTable.id == entry_id_int
            )

            if entries.count() == 0:
                print("Entry {} is not present in the database".format(entry_id))
                return False

            entry = entries.first()
            entry.bookmarked = False

            session.commit()
            print("Unbookmarked")

        return True
