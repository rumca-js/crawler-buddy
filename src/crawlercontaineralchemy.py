from sqlalchemy import create_engine, Column, Integer, DateTime, func, and_, or_, event
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.types import JSON
import os
from .crawlercontainer import *
from webtoolkit import request_to_json, json_to_request


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


class CrawlerContainerAlchemy:
    """
    Maintains history of crawls in SQLite database.
    """

    def __init__(self, db_path="crawlhistory.db"):
        db_exists = os.path.exists(db_path)
        self.records_size = 200

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
        request = request_to_json(request)
        if request:
            request["crawler_type"] = None
            request["handler_type"] = None
        return request

    def crawl(self, crawl_type, request: dict):
        request = self._request_to_json(request)

        if not isinstance(request, dict):
            raise TypeError("request must be a dict")
        if "url" not in request:
            raise ValueError("request must contain 'url'")

        with self.Session() as session:
            record = CrawlHistoryJson(crawl_type=crawl_type, request=request)
            session.add(record)
            session.commit()

            return record.crawl_id

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
            if request:
                conditions.append( and_(
                    CrawlHistoryJson.request["url"].as_string() == request["url"],
                    CrawlHistoryJson.request["crawler_name"].as_string() == request["crawler_name"],
                    CrawlHistoryJson.request["handler_name"].as_string() == request["handler_name"]))

            if not conditions:
                raise ValueError( "Provide crawl_id or request with url, crawler_name, and handler" )

            if crawl_type:
                conditions.append(CrawlHistoryJson.crawl_type == crawl_type)

            record = query.filter(and_(*conditions)).first()
            return record

    def update_by_url(self, url: str, new_json: dict):
        if not isinstance(new_json, dict):
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
            session.commit()
            return True

    def update(self, crawl_id, data: dict):
        #if not isinstance(data, dict):
        #    raise TypeError("new_json must be a dict")

        with self.Session() as session:
            record = (
                session.query(CrawlHistoryJson)
                .filter(CrawlHistoryJson.crawl_id == crawl_id)
                .first()
            )
            if not record:
                return False

            record.data = data
            session.commit()
            return True

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
            # Subquery: get IDs of the newest 200 records
            subquery = (
                session.query(CrawlHistoryJson.crawl_id)
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
