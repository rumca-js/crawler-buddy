from utils.sqlmodel import (
    SqlModel,
    EntriesTable,
    EntriesTableController,
    SourcesTable,
    SourcesTableController,
    SourceOperationalData,
    SourceOperationalDataController,
)


class SourceDataBuilder(object):
    def __init__(self, conn, link=None, link_data=None, manual_entry=False):
        self.conn = conn
        self.link = link
        self.link_data = link_data

    def get_session(self):
        return self.conn.get_session()

    def build(self, link=None, link_data=None, manual_entry=False):
        if link_data:
            self.link_data = link_data
        if link:
            self.link = link

        if self.link_data:
            return self.build_from_props()
        elif self.link:
            return self.build_from_link()

    def build_from_link(self):
        rss_url = self.link

        if rss_url.endswith("/"):
            rss_url = rss_url[:-1]

        h = Url(rss_url)
        if not h.is_valid():
            return

        self.link_data = h.get_properties()

        return self.build_from_props()

    def build_from_props(self):
        result = False

        Session = self.get_session()
        with Session() as session:
            table = SourcesTable(**self.link_data)

            session.add(table)
            session.commit()

            result = True

        return result

    def import_source(self, link_data=None):
        """
        importing might be different than building from scratch
        """
        self.build(link_data=link_data)
        print("import test")
