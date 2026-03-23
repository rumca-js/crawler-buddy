from sqlalchemy import create_engine, Column, Integer, DateTime, func
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.types import JSON
import os


Base = declarative_base()


class CrawlHistoryJson(Base):
    __tablename__ = "crawl_history"

    crawl_id = Column(Integer, primary_key=True)
    crawl_type = Column(Integer)
    request = Column(JSON, nullable=False)
    data = Column(JSON, nullable=True)
    date_created = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class CrawlerContainerAlchemy:
    """
    Maintains history of crawls in SQLite database.
    """

    def __init__(self, db_path="crawlhistory.db"):
        db_exists = os.path.exists(db_path)

        self.engine = create_engine(f"sqlite:///{db_path}", echo=False)
        self.Session = sessionmaker(bind=self.engine)

        if not db_exists:
            Base.metadata.create_all(self.engine)
        else:
            Base.metadata.create_all(self.engine)

    def add(self, request_json: dict):
        if not isinstance(request_json, dict):
            raise TypeError("request_json must be a dict")
        if "url" not in request_json:
            raise ValueError("request_json must contain 'url'")

        with self.Session() as session:
            record = CrawlHistoryJson(request=request_json)
            session.add(record)
            session.commit()

    def get_by_url(self, url: str):
        with self.Session() as session:
            return (
                session.query(CrawlHistoryJson)
                .filter(CrawlHistoryJson.request["url"].as_string() == url)
                .first()
            )

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

    def delete_by_url(self, url: str):
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
