from src.webtools import HtmlPage, calculate_hash, FeedReader

from tests.fake.reddit import reddit_rss_text

from tests.fake.youtube import (
    webpage_youtube_airpano_feed,
    webpage_samtime_youtube_rss,
)

from tests.fake.thehill import (
    thehill_rss,
)
from tests.fake.hackernews import (
    webpage_hackernews_rss,
)

from .fakeinternet import FakeInternetTestCase, MockRequestCounter


class FeedreaderTest(FakeInternetTestCase):
    def setUp(self):
        self.disable_web_pages()

    def test_reddit(self):
        MockRequestCounter.mock_page_requests = 0

        # default language
        p = FeedReader.parse(reddit_rss_text)
        self.assertEqual(p.feed.title, "RSS - Really Simple Syndication")
        self.assertEqual(p.feed.link, "https://www.reddit.com/r/rss/.rss")
        self.assertEqual(len(p.entries), 26)

    def test_youtube(self):
        MockRequestCounter.mock_page_requests = 0

        # default language
        p = FeedReader.parse(webpage_youtube_airpano_feed)
        self.assertEqual(p.feed.title, "AirPano VR")
        self.assertEqual(
            p.feed.link,
            "http://www.youtube.com/feeds/videos.xml?channel_id=UCUSElbgKZpE4Xdh5aFWG-Ig",
        )
        self.assertEqual(len(p.entries), 15)

    def test_the_hill(self):
        MockRequestCounter.mock_page_requests = 0

        # default language
        p = FeedReader.parse(thehill_rss)
        self.assertEqual(p.feed.title, "The Hill News")
        self.assertEqual(p.feed.link, "https://thehill.com")
        self.assertEqual(len(p.entries), 100)

    def test_hacker_news(self):
        MockRequestCounter.mock_page_requests = 0

        # default language
        p = FeedReader.parse(webpage_hackernews_rss)
        self.assertEqual(p.feed.title, "Hacker News: Front Page")
        self.assertEqual(p.feed.link, "https://news.ycombinator.com/")

        self.assertEqual(len(p.entries), 20)

        self.assertTrue(p.entries[0].description.find("Article URL") >= 0)
