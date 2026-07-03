import threading
import os

from sqlalchemy import create_engine, Column, Integer, DateTime, func, and_, or_, event, select
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.types import JSON

from webtoolkit import request_to_json, json_to_request, PageRequestObject
from .crawlercontainer import *


Base = declarative_base()


class CrawlHistoryJson(Base):
    __tablename__ = "crawl_history"

    crawl_id = Column(Integer, primary_key=True)
    crawl_type = Column(Integer)
    request = Column(JSON, nullable=False)
    data = Column(JSON, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    def get_url(self):
        request = json_to_request(self.request)
        if request:
            return request.url

    def get_request(self):
        return json_to_request(self.request)

    def is_response(self):
        return self.data is not None

    def is_expired(self):
        return False


class CrawlerContainerAlchemy:
    """
    Maintains history of crawls in SQLite database.
    """

    def __init__(self, time_cache_m=10, records_size=500, db_path="crawlhistory.db"):
        self.lock = threading.Lock()           # protects running_ids
        self.crawl_index = 0

        db_exists = os.path.exists(db_path)

        self.records_size = records_size
        self.no_history_crawls = 0
        self.time_cache_m = time_cache_m

        self.engine = create_engine(f"sqlite:///{db_path}", echo=False)

        # Enable WAL mode
        @event.listens_for(self.engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA journal_mode=WAL;")
            cursor.close()

        self.Session = sessionmaker(bind=self.engine)

        # Create tables if they don't exist
        Base.metadata.create_all(self.engine)

    def _request_to_json(self, request):
        request_new = request_to_json(request)
        if request_new:
            #request_new["crawler_type"] = None
            #request_new["handler_type"] = None

            if request.crawler_name is None:
                request_new["crawler_name"] = ""
            else:
                request_new["crawler_name"] = request.crawler_name
            if request.handler_name is None:
                request_new["handler_name"] = ""
            else:
                request_new["handler_name"] = request.handler_name

        return request_new

    def crawl(self, crawl_type, request: dict):
        request = self._request_to_json(request)

        self.expire_old()
        self.trim_size()

        if self.get_size() >= self.records_size:
            self.remove_one_history()

        if self.get_size() >= self.records_size:
            return

        if not isinstance(request, dict):
            raise TypeError("request must be a dict")
        if "url" not in request:
            raise ValueError("request must contain 'url'")

        with self.Session() as session:
            record = CrawlHistoryJson(crawl_type=crawl_type, request=request)
            session.add(record)
            session.commit()

            return record.crawl_id

    def add(self, crawl_type=None, request=None, data=None, crawl_id=None):
        if request and isinstance(request, PageRequestObject):
            request = self._request_to_json(request)

        item_updated = False
        if crawl_id:
            crawl_item = self.get(crawl_id=crawl_id)
            if crawl_item:
                self.update(crawl_id, data)
                item_updated = True

        if not item_updated:
            crawl_item = self.get(request=request)
            if crawl_item:
                self.update(crawl_item.crawl_id, data)
                item_updated = True

        if not item_updated:
            with self.lock:
                self.crawl_index += 1
                crawl_id = self.crawl_index

                with self.Session() as session:
                    record = CrawlHistoryJson(crawl_id=crawl_id, crawl_type=crawl_type, request=request, data=data)
                    session.add(record)
                    session.commit()

                    return record.crawl_id

        self.expire_old()
        self.trim_size()

        if crawl_item:
            return crawl_item.crawl_id

    def remove_one_history(self):
        with self.Session() as session:
            record = (
                session.query(CrawlHistoryJson)
                .filter(CrawlHistoryJson.data.is_not(None))
                .order_by(CrawlHistoryJson.timestamp.asc())
                .first()
            )
            if not record:
                return False

            session.delete(record)
            session.commit()
            return True

    def get_by_url(self, url: str):
        with self.Session() as session:
            return (
                session.query(CrawlHistoryJson)
                .filter(CrawlHistoryJson.request["url"].as_string() == url)
                .first()
            )

    def find(self, crawl_id=None, crawl_type=None, request=None):
        record = self.get(crawl_id=crawl_id, crawl_type=crawl_type, request=request)
        return record.crawl_id if record else None

    def get(self, crawl_id=None, crawl_type=None, request=None):
        if request and isinstance(request, PageRequestObject):
            request = self._request_to_json(request)

        with self.Session() as session:
            query = session.query(CrawlHistoryJson)

            conditions = []

            # 1: crawl_id match
            if crawl_id is not None:
                conditions.append(CrawlHistoryJson.crawl_id == crawl_id)
                record = query.filter(or_(*conditions)).first()
                return record

            # 2: (url AND crawler_name AND handler_name)
            if request is not None:
                conditions.append( and_(
                    CrawlHistoryJson.request["url"].as_string() == request["url"],
                    CrawlHistoryJson.request["crawler_name"].as_string() == request["crawler_name"],
                    CrawlHistoryJson.request["handler_name"].as_string() == request["handler_name"]))

            if conditions is []:
                raise ValueError( "Provide crawl_id or request with url, crawler_name, and handler" )

            if crawl_type:
                conditions.append(CrawlHistoryJson.crawl_type == crawl_type)

            record = query.filter(and_(*conditions)).first()
            return record

    def update_by_url(self, url: str, new_json: dict, timestamp=None):
        if new_json and not isinstance(new_json, dict):
            raise TypeError("new_json must be a dict")

        with self.Session() as session:
            record = (
                session.query(CrawlHistoryJson)
                .filter(CrawlHistoryJson.request["url"].as_string() == url)
                .first()
            )
            if not record:
                return False

            record.data = new_json
            if timestamp:
                record.timestamp = timestamp
            else:
                record.timestamp = datetime.now()
            session.commit()
            return True

    def update(self, crawl_id, data: dict, timestamp=None):
        #if not isinstance(data, dict):
        #    raise TypeError("new_json must be a dict")

        try:
            with self.Session() as session:
                record = (
                    session.query(CrawlHistoryJson)
                    .filter(CrawlHistoryJson.crawl_id == crawl_id)
                    .first()
                )
                if not record:
                    return False

                record.data = data

                if timestamp:
                    record.timestamp = timestamp
                else:
                    record.timestamp = datetime.now()

                session.commit()
                return True
        except Exception as E:
            with open("debug.txt", "w") as fh:
                fh.write(str(data))

            raise E

    def remove_by_url(self, url: str):
        with self.Session() as session:
            record = (
                session.query(CrawlHistoryJson)
                .filter(CrawlHistoryJson.data["url"].as_string() == url)
                .first()
            )
            if not record:
                return False

            session.delete(record)
            session.commit()
            return True

    def remove(self, crawl_id):
        with self.Session() as session:
            record = (
                session.query(CrawlHistoryJson)
                .filter(CrawlHistoryJson.crawl_id == crawl_id)
                .first()
            )
            if not record:
                return False

            session.delete(record)
            session.commit()
            return True

    def clear(self):
        with self.Session() as session:
            session.query(CrawlHistoryJson).delete()
            session.commit()

    def trim_size(self):
        with self.Session() as session:
            cutoff = datetime.now() - timedelta(seconds=self.time_cache_m * 60)

            # Subquery: get IDs of the newest 200 records (or do not have response)
            subquery = (
                session.query(CrawlHistoryJson.crawl_id)
                .filter(or_(CrawlHistoryJson.timestamp >= cutoff, CrawlHistoryJson.data.is_(None)))
                .order_by(CrawlHistoryJson.timestamp.desc())
                .limit(self.records_size)
                .subquery()
            )

            # Delete everything NOT in the newest 200
            deleted = (
                session.query(CrawlHistoryJson)
                .filter(~CrawlHistoryJson.crawl_id.in_(select(subquery)))
                .delete(synchronize_session=False)
            )

            session.commit()
            return deleted

    def expire_old(self):
        """
        Remove entries older than the time_cache window.
        Do not remove things that are in queue
        """
        cutoff = datetime.now() - timedelta(seconds=self.time_cache_m * 60)

        with self.Session() as session:
            rows = session.query(CrawlHistoryJson).filter(and_(CrawlHistoryJson.timestamp < cutoff, CrawlHistoryJson.data.is_not(None))).order_by(CrawlHistoryJson.timestamp.asc())

            for row in rows:
                session.delete(row)
                session.commit()

    def get_size(self):
        """returns count of the table"""
        with self.Session() as session:
            return session.query(func.count(CrawlHistoryJson.crawl_id)).scalar()

    def get_all_items(self):
        """returns all records in the table"""
        with self.Session() as session:
            return session.query(CrawlHistoryJson).all()

    def get_queued_items(self):
        """return records without data (null)"""
        with self.Session() as session:
            return session.query(CrawlHistoryJson).filter(CrawlHistoryJson.data.is_(None)).all()

    def get_ready_items(self):
        """return records with data (not null)"""
        with self.Session() as session:
            return session.query(CrawlHistoryJson).filter(CrawlHistoryJson.data.is_not(None)).all()

    def set_time_cache(self, time_cache_m):
        self.time_cache_m = time_cache_m

    def set_records_size(self, row_size):
        self.records_size = row_size

    def get_no_crawls(self):
        return self.get_size()

    def close_item(self, crawl_item):
        self.no_history_crawls += 1
