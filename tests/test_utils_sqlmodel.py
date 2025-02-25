from pathlib import Path
from sqlalchemy import (
    create_engine,
)

from utils import (
   SqlModel,
   EntriesTableController,
   EntriesTable,
   SourcesTable,
   SourcesTableController,
)

from .fakeinternet import FakeInternetTestCase, MockRequestCounter


class SqlModelTest(FakeInternetTestCase):
    """
    Tests most important aspects of display:
    header, footer, index
    """

    def setUp(self):
        self.disable_web_pages()

    def test_add_entry(self):
        path = Path("test.db")
        if path.exists():
            path.unlink()

        engine = create_engine("sqlite:///test.db")

        db = SqlModel(database_file="test.db", engine=engine)

        controller = EntriesTableController(db)

        entry = {
                "title" : "Title",
                "link" : "https://www.youtube.com",
                "description" : "description",
        }

        controller.add_entry(entry)

        count_entries = 0
        count_sources = 0

        Session = db.get_session()
        with Session() as session:
            q = session.query(EntriesTable)
            count_entries = q.count()

            q = session.query(SourcesTable)
            count_sources = q.count()

        db.close()

        self.assertEqual(count_entries, 1)
        self.assertEqual(count_sources, 0)

    def test_add_source(self):
        path = Path("test.db")
        if path.exists():
            path.unlink()

        engine = create_engine("sqlite:///test.db")

        db = SqlModel(database_file="test.db", engine=engine)

        controller = SourcesTableController(db)

        source = {
                "title" : "Title",
                "url" : "https://www.youtube.com",
        }

        controller.add(source)

        count_entries = 0
        count_sources = 0

        Session = db.get_session()
        with Session() as session:
            q = session.query(EntriesTable)
            count_entries = q.count()

            q = session.query(SourcesTable)
            count_sources = q.count()

        db.close()

        self.assertEqual(count_entries, 0)
        self.assertEqual(count_sources, 1)
