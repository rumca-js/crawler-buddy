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
    YouTubeJsonHandler,
    Url,
    WebConfig,
)

from webtoolkit import (
    PageRequestObject,
    PageResponseObject,
    WebLogger,
    ResponseHeaders,
    CrawlerInterface,
    YouTubeChannelHandler,
    CrawlerInterface,
)
from webtoolkit.tests.mocks import (
    MockRequestCounter,
    MockCrawler,
)

from webtoolkit.tests.fakeinternetcontents import (
    webpage_with_real_rss_links,
    webpage_simple_rss_page,
    webpage_old_pubdate_rss,
    webpage_no_pubdate_rss,
    webpage_html_favicon,
    webpage_with_rss_link_rss_contents,
    webpage_html_casinos,
    webpage_html_canonical_1,
)
from webtoolkit.tests.fake.geekwirecom import (
    geekwire_feed,
)
from webtoolkit.tests.fake.youtube import (
    youtube_robots_txt,
    youtube_sitemap_sitemaps,
    youtube_sitemap_product,
    webpage_youtube_airpano_feed,
    webpage_samtime_odysee,
    webpage_samtime_youtube_rss,
    youtube_channel_html_linus_tech_tips,
    youtube_channel_rss_linus_tech_tips,
)
from webtoolkit.tests.fake.robotstxtcom import (
    robots_txt_example_com_robots,
)
from webtoolkit.tests.fake.codeproject import (
    webpage_code_project_rss,
)
from webtoolkit.tests.fake.opmlfile import (
    opml_file,
)
from webtoolkit.tests.fake.hackernews import (
    webpage_hackernews_rss,
    hacker_news_item,
)
from webtoolkit.tests.fake.warhammercommunity import (
    warhammer_community_rss,
)
from webtoolkit.tests.fake.thehill import (
    thehill_rss,
)
from webtoolkit.tests.fake.reddit import (
    reddit_rss_text,
    reddit_entry_json,
    reddit_subreddit_json,
)
from webtoolkit.tests.fake.githubcom import (
    github_json,
)
from webtoolkit.tests.fake.returndislike import (
    return_dislike_json,
)
from webtoolkit.tests.fake.firebog import (
    firebog_adguard_list,
    firebog_w3kbl_list,
    firebog_tick_lists,
    firebog_malware,
)
from webtoolkit.tests.fake.instance import (
    instance_entries_json,
    instance_sources_json_empty,
    instance_entries_json_empty,
    instance_entries_source_100_json,
    instance_source_100_url,
    instance_source_100_json,
    instance_source_101_json,
    instance_source_102_json,
    instance_source_103_json,
    instance_source_104_json,
    instance_source_105_json,
    instance_sources_page_1,
    instance_sources_page_2,
)


class FlaskArgs(object):
    def __init__(self):
        self._map = {}

    def get(self, key):
        if key in self._map:
            return self._map[key]

    def set(self, key, value):
        self._map[key] = value

    def __contains__(self, key):
        return key in self._map

    def __getitem__(self, key):
        return self._map[key]


class FlaskRequest(object):
    def __init__(self, host):
        self.host = host
        self.args = FlaskArgs()

    def set(self, key, value):
        self.args.set(key, value)


class YtdlpCrawlerMock(CrawlerInterface):

    def run(self):
        from utils.programwrappers import ytdlp

        MockRequestCounter.requested(self.request.url, crawler_data=self.request)

        code = (self.request.url)

        yt_text = ""
        status_code = 200

        if code == "1234":
            yt_text = """{"_filename" : "1234 test file name",
            "title" : "1234 test title",
            "description" : "1234 test description",
            "channel_url" : "https://youtube.com/channel/1234-channel",
            "channel" : "1234-channel",
            "channel_follower_count" : 5,
            "id" : "1234-id",
            "channel_id" : "1234-channel-id",
            "thumbnail" : "https://youtube.com/files/1234-thumbnail.png",
            "upload_date" : "${date}",
            "view_count" : "2",
            "live_status" : "False"
            }""".replace("${date}", self.get_now())
        if code == "666":
            status_code = 401
        if code == "555555":
            yt_text = """{"_filename" : "555555 live video.txt",
            "title" : "555555 live video",
            "description" : "555555 live video description",
            "channel_url" : "https://youtube.com/channel/test.txt",
            "channel" : "JoYoe",
            "channel_follower_count" : 5,
            "id" : "3433",
            "channel_id" : "JoYoe",
            "thumbnail" : "https://youtube.com/files/whatever.png",
            "upload_date" : "${date}",
            "view_count" : "2",
            "live_status" : "True"
            }""".replace("${date}", self.get_now())
        if code == "archived":
            yt_text = """{"_filename" : "555555 live video.txt",
            "title" : "555555 live video",
            "description" : "555555 live video description",
            "channel_url" : "https://youtube.com/channel/test.txt",
            "channel" : "JoYoe",
            "channel_follower_count" : 5,
            "id" : "3433",
            "channel_id" : "JoYoe",
            "thumbnail" : "https://youtube.com/files/whatever.png",
            "upload_date" : "20231113",
            "view_count" : "2",
            "live_status" : "False"
            }""".replace("${date}", self.get_now())
        else:
            yt_text = """{"_filename" : "test.txt",
            "title" : "test.txt",
            "description" : "test.txt",
            "channel_url" : "https://youtube.com/channel/test.txt",
            "channel" : "JoYoe",
            "channel_follower_count" : 5,
            "id" : "3433",
            "channel_id" : "JoYoe",
            "thumbnail" : "https://youtube.com/files/whatever.png",
            "upload_date" : "${date}",
            "view_count" : "2",
            "live_status" : "False"
            }""".replace("${date}", self.get_now())

        headers = {}
        headers["Content-Type"] = "text/json"

        self.response = PageResponseObject(
            url=self.request.url,
            text=yt_text,
            status_code=status_code,
            encoding="utf-8",
            headers=headers,
            binary=None,
            request_url=self.request.url,
        )

        return self.response

    def is_valid(self):
        return True

    def get_now(self):
        """
        format 20231113
        """
        date = DateUtils.get_datetime_now_utc()
        tuple = DateUtils.get_date_tuple(date)

        return str(tuple[0]) + str(tuple[1]) + str(tuple[2])


class YouTubeChannelHandlerMock(YouTubeChannelHandler):
    def __init__(self, url=None):
        super().__init__(url)

    def get_contents(self):
        if self.dead:
            return


class FakeInternetTestCase(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        MockRequestCounter.reset()
        self.get_response_saved = Url.get_response

    def disable_web_pages(self):
        WebConfig.use_print_logging()

        WebConfig.get_default_crawler = FakeInternetTestCase.get_default_crawler
        WebConfig.get_crawler_from_string = FakeInternetTestCase.get_crawler_from_string

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
