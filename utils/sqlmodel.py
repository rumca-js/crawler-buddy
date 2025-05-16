"""
Library package.

Should be binary compatibile with django model

Right now we are not able to do sO.
"""

from typing import Optional
from sqlalchemy import (
    create_engine,
    Table,
    MetaData,
    select,
    func,
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    delete,
    update,
)
from sqlalchemy.orm import sessionmaker
from datetime import timedelta, datetime, timezone

import sqlalchemy
from sqlalchemy.orm import Session
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from .dateutils import DateUtils


def create_this_engine():
    file_name = "test.db"
    return create_engine("sqlite:///" + file_name)


class SqlConnection(object):
    """
    Simple wrapper for connection
    """

    def __init__(self, database_file="test.db", parser=None):
        self.cursor = None
        self.database_file = database_file

        self.parser = parser

        if not self.create_database():
            print("Could not connect to database")
            return

    def create_database(self):
        file_name = self.get_database_file()

        # try:

        # self.engine = create_engine('sqlite:///'+file_name, echo=True)
        self.engine = create_engine("sqlite:///" + file_name)
        return True

        # except Exception as e:
        #    print(
        #        "Could not create sqlite3 database file:{}. Exception:{}".format(
        #            file_name, str(e)
        #        )
        #    )
        #    return False

    def close(self):
        self.engine.dispose()

    def get_database_file(self):
        return self.database_file


class GenericTable(object):
    def __init__(self, sqlconnection):
        self.conn = sqlconnection

        self.table_name = None
        self.table = None

    def create(self):
        """
        Expected to set self.table
        """
        raise NotImplementedError(
            "GenericTable: create function has not been implemeneted"
        )

    def count(self):
        from sqlalchemy.sql import text

        st = select(func.count()).select_from(text(self.table_name))
        return self.get_connection().execute(st).scalar()

    def select(self):
        query = select(self.table)
        result = self.get_connection().execute(query)
        return result.fetchall()

    def truncate(self):
        if self.table_name:
            truncate_query = sqlalchemy.text("DELETE FROM {}".format(self.table_name))
            self.get_connection().execute(truncate_query)
            self.commit()

    def get_connection(self):
        return self.conn.conn

    def commit(self):
        self.conn.commit()


class Base(DeclarativeBase):
    pass


class EntriesTable(Base):
    __tablename__ = "linkdatamodel"

    id: Mapped[int] = mapped_column(primary_key=True)
    link: Mapped[str] = mapped_column(String(30), unique=True)
    title: Mapped[str]
    description: Mapped[Optional[str]]
    thumbnail: Mapped[Optional[str]]
    language: Mapped[Optional[str]]
    age: Mapped[int] = mapped_column(default=0)
    date_created = mapped_column(DateTime(timezone=True), nullable=True)
    date_published = mapped_column(DateTime(timezone=True), nullable=True)
    date_update_last = mapped_column(DateTime(timezone=True), nullable=True)
    date_dead_since = mapped_column(DateTime(timezone=True), nullable=True)
    date_last_modified = mapped_column(DateTime(timezone=True), nullable=True)
    status_code: Mapped[int] = mapped_column(default=0)
    page_rating: Mapped[int] = mapped_column(default=0)
    page_rating_votes: Mapped[int] = mapped_column(default=0)
    page_rating_contents: Mapped[int] = mapped_column(default=0)
    bookmarked: Mapped[bool] = mapped_column(default=False)
    permanent: Mapped[bool] = mapped_column(default=False)
    author: Mapped[Optional[str]]
    album: Mapped[Optional[str]]
    # advanced / foreign
    source: Mapped[Optional[int]]


class EntriesTableController(object):
    def __init__(self, db, session=None):
        self.conn = db
        self.session = session

    def get_session(self):
        if not self.session:
            return self.conn.get_session()
        else:
            return self.session

    def remove(self, days):
        now = datetime.now(timezone.utc)
        limit = now - timedelta(days=days)

        Session = self.get_session()

        with Session() as session:
            entries = session.query

            query = delete(EntriesTable).where(
                EntriesTable.date_published < limit, EntriesTable.bookmarked == False
            )
            session.execute(query)
            session.commit()

    def add_entry(self, entry):
        # Get the set of column names from EntriesTable
        valid_columns = {column.name for column in EntriesTable.__table__.columns}

        # Remove keys that are not in EntriesTable
        entry = {key: value for key, value in entry.items() if key in valid_columns}

        entry_obj = EntriesTable(**entry)

        Session = self.get_session()
        with Session() as session:
            session.add(entry_obj)
            session.commit()


class SourcesTable(Base):
    __tablename__ = "sourcedatamodel"

    id: Mapped[int] = mapped_column(primary_key=True)
    enabled: Mapped[bool] = mapped_column(default=True)
    url: Mapped[str] = mapped_column(unique=True)
    title: Mapped[str]
    age: Mapped[int] = mapped_column(default=0)
    category: Mapped[Optional[str]]
    subcategory: Mapped[Optional[str]]
    export_to_cms: Mapped[bool] = mapped_column(default=True)
    favicon: Mapped[Optional[str]]
    fetch_period: Mapped[Optional[int]]
    language: Mapped[Optional[str]]
    proxy_location: Mapped[Optional[str]]
    remove_after_days: Mapped[Optional[int]]
    source_type: Mapped[Optional[str]]
    category_name: Mapped[Optional[str]]
    subcategory_name: Mapped[Optional[str]]


class SourcesTableController(object):
    def __init__(self, db, session=None):
        self.conn = db
        self.session = session

    def get_session(self):
        if not self.session:
            return self.conn.get_session()
        else:
            return self.session

    def get_all(self):
        sources = []

        Session = self.get_session()
        with Session() as session:
            sources = session.query(SourcesTable).all()

        return sources

    def is_source(self, id=None, url=None):
        is_source = False
        Session = self.get_session()

        with Session() as session:
            if id:
                sources = (
                    session.query(SourcesTable)
                    .filter(SourcesTable.id == int(id))
                    .count()
                )
                if sources != 0:
                    is_source = True
            if url:
                sources = (
                    session.query(SourcesTable).filter(SourcesTable.url == url).count()
                )
                if sources != 0:
                    is_source = True

        return is_source

    def add(self, source):
        # Get the set of column names from EntriesTable
        valid_columns = {column.name for column in SourcesTable.__table__.columns}

        # Remove keys that are not in EntriesTable
        source = {key: value for key, value in source.items() if key in valid_columns}

        source_obj = SourcesTable(**source)

        Session = self.get_session()
        with Session() as session:
            session.add(source_obj)
            session.commit()


class SourceOperationalData(Base):
    __tablename__ = "sourceoperationaldata"

    id: Mapped[int] = mapped_column(primary_key=True)
    date_fetched = mapped_column(DateTime, nullable=True)
    source: Mapped[int]


class SourceOperationalDataController(object):
    def __init__(self, db, session=None):
        self.conn = db
        self.session = session

    def get_session(self):
        if not self.session:
            return self.conn.get_session()
        else:
            return self.session

    def is_fetch_possible(self, source, date_now, limit_seconds=60 * 10):
        Session = self.get_session()
        with Session() as session:
            rows = (
                session.query(SourceOperationalData)
                .filter(SourceOperationalData.source == source.id)
                .all()
            )

            if len(rows) == 0:
                return True

            row = rows[0]

            source_datetime = row.date_fetched

            diff = date_now - source_datetime

            if diff.total_seconds() > limit_seconds:
                return True
            return False

    def set_fetched(self, source, date_now):
        Session = self.get_session()
        with Session() as session:
            op_data = (
                session.query(SourceOperationalData)
                .filter(SourceOperationalData.source == source.id)
                .all()
            )
            if len(op_data) == 0:
                obj = SourceOperationalData(date_fetched=date_now, source=source.id)
                session.add(obj)
                session.commit()
            else:
                op_data = op_data[0]
                op_data.date_fetched = date_now
                session.commit()


class UserTags(Base):
    __tablename__ = "usertags"

    id: Mapped[int] = mapped_column(primary_key=True)
    date = mapped_column(DateTime)
    tag: Mapped[str] = mapped_column(String(1000))

    entry_object: Mapped[Optional[int]]
    user_object: Mapped[Optional[int]]


class UserBookmarks(Base):
    __tablename__ = "userbookmarks"
    id: Mapped[int] = mapped_column(primary_key=True)

    date_bookmarked = mapped_column(DateTime)

    entry_object: Mapped[Optional[int]]
    user_object: Mapped[Optional[int]]


class UserVotes(Base):
    __tablename__ = "uservotes"
    id: Mapped[int] = mapped_column(primary_key=True)

    user: Mapped[str] = mapped_column(String(1000))
    vote: Mapped[int] = mapped_column(default=0)

    entry_object: Mapped[Optional[int]]
    user_object: Mapped[Optional[int]]


class ReadMarkers(Base):
    __tablename__ = "readmarkers"
    id: Mapped[int] = mapped_column(primary_key=True)
    read_date = mapped_column(DateTime)
    source_object: Mapped[Optional[int]]

    def set(session, source=None):
        if not source:
            markers = session.query(ReadMarkers)
            if markers.count() == 0:
                m = ReadMarkers(read_date=DateUtils.get_datetime_now_utc())
                session.add(m)
                session.commit()
            else:
                marker = markers.first()
                marker.read_date = DateUtils.get_datetime_now_utc()
                session.commit()
        else:
            markers = session.query(ReadMarkers, source_object == source.id)
            if markers.count() == 0:
                m = ReadMarkers(
                    read_date=DateUtils.get_datetime_now_utc(), source_object=source.id
                )
                session.add(m)
                session.commit()
            else:
                marker = markers.first()
                marker.read_date = DateUtils.get_datetime_now_utc()
                session.commit()


class SqlModel(object):
    def __init__(self, database_file="test.db", parser=None, engine=None):
        self.db_file = database_file

        if not engine:
            self.engine = create_engine("sqlite:///" + self.db_file)
        else:
            self.engine = engine

        Base.metadata.create_all(self.engine)

    def get_session(self):
        _SessionFactory = sessionmaker(bind=self.engine)
        return _SessionFactory

    def close(self):
        if self.engine:
            self.engine.dispose()
