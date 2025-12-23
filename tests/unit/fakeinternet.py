"""
This module provides replacement for the Internet.

 - when test make requests to obtain a page, we return artificial data here
 - when there is a request to obtain youtube JSON data, we provide artificial data, etc.
"""

import logging
import unittest
import traceback

from utils.dateutils import DateUtils
from src.webtools import (
    YouTubeVideoHandlerJson,
    Url,
    WebConfig,
)

from webtoolkit import (
    PageRequestObject,
    PageResponseObject,
    CrawlerInterface,
    YouTubeChannelHandler,
    YouTubeVideoHandler,
)
from webtoolkit.tests.mocks import (
    MockRequestCounter,
    MockCrawler,
    YtdlpCrawlerMock,
)


class FakeInternetTestCase(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        MockRequestCounter.reset()
        self.get_response_saved = Url.get_response

    def disable_web_pages(self):
        WebConfig.use_print_logging()

        WebConfig.get_default_crawler = FakeInternetTestCase.get_default_crawler
        WebConfig.get_crawler_from_string = FakeInternetTestCase.get_crawler_from_string

        Url.get_request_for_url = FakeInternetTestCase.get_request_for_url
        Url.get_request_for_request = FakeInternetTestCase.get_request_for_request

    def get_response(self):
        if self.request.crawler_name == "YtdlpCrawler":
            self.request.crawler_type = YtdlpCrawlerMock(request=self.request)
        return self.get_response_saved()

    def get_default_crawler(url):
        data = {}
        data["name"] = "MockCrawler"
        data["crawler"] = MockCrawler(url = url)
        data["settings"] = {"timeout_s" : 20}

        return data

    def get_request_for_url(self, url):
        request = PageRequestObject(url)
        request.crawler_name = "MockCrawler"
        request.crawler_type = MockCrawler(url)
        return request

    def get_request_for_request(self, request):
        if self.request.crawler_name == "YtdlpCrawler":
            self.request.crawler_type = YtdlpCrawlerMock(request=self.request)
        else:
            self.request.crawler_name == "MockCrawler"
            self.request.crawler_type = MockCrawler(request=self.request)

        return request

    def get_crawler_from_string(crawler_string):
        if not crawler_string:
            return

        if crawler_string == "MockCrawler":
            return MockCrawler

        if crawler_string == "YtdlpCrawler":
            return YtdlpCrawlerMock

        crawlers = WebConfig.get_crawlers_raw()
        for crawler in crawlers:
            if crawler.__name__ == crawler_string:
                return crawler

    def setup_configuration(self):
        # each suite should start with a default configuration entry
        c = Configuration.get_object()
        c.config_entry = ConfigurationEntry.get()

        c.config_entry.enable_keyword_support = True
        c.config_entry.enable_domain_support = True
        c.config_entry.accept_domain_links = True
        c.config_entry.accept_non_domain_links = True
        c.config_entry.new_entries_merge_data = False
        c.config_entry.new_entries_use_clean_data = False
        c.config_entry.default_source_state = False
        c.config_entry.auto_create_sources = False
        c.config_entry.auto_scan_new_entries = False
        c.config_entry.enable_link_archiving = False
        c.config_entry.enable_source_archiving = False
        c.config_entry.track_user_actions = False
        c.config_entry.track_user_searches = False
        c.config_entry.track_user_navigation = False
        c.config_entry.days_to_move_to_archive = 100
        c.config_entry.days_to_remove_links = 0
        c.config_entry.respect_robots_txt = False
        c.config_entry.whats_new_days = 7
        c.config_entry.keep_domain_links = True
        c.config_entry.entry_update_via_internet = True

        c.config_entry.save()

        c.apply_robots_txt()

    def get_user(
        self, username="test_username", password="testpassword", is_superuser=False
    ):
        """
        TODO test cases should be rewritten to use names as follows:
         - test_superuser
         - test_staff
         - test_authenticated
        """
        users = User.objects.filter(username=username)
        if users.count() > 0:
            self.user = users[0]
            self.user.username = username
            self.user.password = password
            self.user.is_superuser = is_superuser
            self.user.save()
        else:
            self.user = User.objects.create_user(
                username=username, password=password, is_superuser=is_superuser
            )

        return self.user

    def print_errors(self):
        infos = AppLogging.objects.filter(level=int(logging.ERROR))
        for info in infos:
            print("Error: {}".format(info.info_text))

    def no_errors(self):
        infos = AppLogging.objects.filter(level=int(logging.ERROR))
        return infos.count() == 0

    def create_example_data(self):
        self.create_example_sources()
        self.create_example_links()
        self.create_example_domains()
        self.create_example_exports()

    def create_example_sources(self):
        source1 = SourceDataController.objects.create(
            url="https://youtube.com",
            title="YouTube",
            category="No",
            subcategory="No",
            export_to_cms=True,
        )
        source2 = SourceDataController.objects.create(
            url="https://linkedin.com",
            title="LinkedIn",
            category="No",
            subcategory="No",
            export_to_cms=False,
        )
        return [source1, source2]

    def create_example_links(self):
        """
        All entries are outdated
        """
        entry1 = LinkDataController.objects.create(
            source_url="https://youtube.com",
            link="https://youtube.com?v=bookmarked",
            title="The first link",
            source=source_youtube,
            bookmarked=True,
            date_published=DateUtils.from_string("2023-03-03;16:34", "%Y-%m-%d;%H:%M"),
            language="en",
        )
        entry2 = LinkDataController.objects.create(
            source_url="https://youtube.com",
            link="https://youtube.com?v=nonbookmarked",
            title="The second link",
            source=source_youtube,
            bookmarked=False,
            date_published=DateUtils.from_string("2023-03-03;16:34", "%Y-%m-%d;%H:%M"),
            language="en",
        )
        entry3 = LinkDataController.objects.create(
            source_url="https://youtube.com",
            link="https://youtube.com?v=permanent",
            title="The first link",
            source=source_youtube,
            permanent=True,
            date_published=DateUtils.from_string("2023-03-03;16:34", "%Y-%m-%d;%H:%M"),
            language="en",
        )

        return [entry1, entry2, entry3]

    def create_example_domains(self):
        DomainsController.add("https://youtube.com?v=nonbookmarked")

        DomainsController.objects.create(
            protocol="https",
            domain="youtube.com",
            category="testCategory",
            subcategory="testSubcategory",
        )
        DomainCategories.objects.all().delete()
        DomainSubCategories.objects.all().delete()

    def create_example_keywords(self):
        datetime = KeyWords.get_keywords_date_limit() - timedelta(days=1)
        keyword = KeyWords.objects.create(keyword="test")
        keyword.date_published = datetime
        keyword.save()

        return [keyword]

    def create_example_exports(self):
        export1 = DataExport.objects.create(
            export_type=DataExport.EXPORT_TYPE_GIT,
            export_data=DataExport.EXPORT_DAILY_DATA,
            local_path=".",
            remote_path=".",
            export_entries=True,
            export_entries_bookmarks=True,
            export_entries_permanents=True,
            export_sources=True,
        )

        export2 = DataExport.objects.create(
            export_type=DataExport.EXPORT_TYPE_GIT,
            export_data=DataExport.EXPORT_YEAR_DATA,
            local_path=".",
            remote_path=".",
            export_entries=True,
            export_entries_bookmarks=True,
            export_entries_permanents=True,
            export_sources=True,
        )

        export3 = DataExport.objects.create(
            export_type=DataExport.EXPORT_TYPE_GIT,
            export_data=DataExport.EXPORT_NOTIME_DATA,
            local_path=".",
            remote_path=".",
            export_entries=True,
            export_entries_bookmarks=True,
            export_entries_permanents=True,
            export_sources=True,
        )

        return [export1, export2, export3]

    def create_example_permanent_data(self):
        p1 = AppLogging.objects.create(info="info1", level=10, user="test")
        p1.date = DateUtils.from_string("2023-03-03;16:34", "%Y-%m-%d;%H:%M")
        p1.save()

        p2 = AppLogging.objects.create(info="info2", level=10, user="test")
        p2.date = DateUtils.from_string("2023-03-03;16:34", "%Y-%m-%d;%H:%M")
        p2.save()

        p3 = AppLogging.objects.create(info="info3", level=10, user="test")
        p3.date = DateUtils.from_string("2023-03-03;16:34", "%Y-%m-%d;%H:%M")
        p3.save()

        return [p1, p2, p3]
