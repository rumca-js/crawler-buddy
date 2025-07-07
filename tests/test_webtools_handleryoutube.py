from utils.dateutils import DateUtils
from src.webtools import (
   YouTubeVideoHandler,
   YouTubeChannelHandler,
   YouTubeJsonHandler,
   Url,
)

from tests.fakeinternet import (
   FakeInternetTestCase, MockRequestCounter, YouTubeJsonHandlerMock
)


class YouTubeJsonHandlerTest(FakeInternetTestCase):
    def setUp(self):
        self.disable_web_pages()

    def test_constructor(self):
        MockRequestCounter.mock_page_requests = 0

        test_link = "https://www.youtube.com/watch?v=123"

        # call tested function
        handler = YouTubeJsonHandlerMock(test_link, url_builder=Url)

        self.assertEqual(handler.url, test_link)
        self.assertEqual(MockRequestCounter.mock_page_requests, 0)

    def test_is_handled_by_video(self):
        MockRequestCounter.mock_page_requests = 0

        handler = YouTubeVideoHandler("https://www.youtube.com/watch?v=1234")
        self.assertTrue(handler.is_handled_by())

    def test_is_handled_by_short(self):
        MockRequestCounter.mock_page_requests = 0

        handler = YouTubeVideoHandler("https://www.youtube.com/shorts/1234")
        self.assertTrue(handler.is_handled_by())

    def test_get_vide_code__video(self):
        MockRequestCounter.mock_page_requests = 0

        handler = YouTubeVideoHandler("https://www.youtube.com/watch?v=1234")
        self.assertEqual(handler.get_video_code(), "1234")

        self.assertEqual(MockRequestCounter.mock_page_requests, 0)

    def test_get_vide_code__short(self):
        MockRequestCounter.mock_page_requests = 0

        handler = YouTubeVideoHandler("https://www.youtube.com/shorts/1234")
        self.assertEqual(handler.get_video_code(), "1234")

        self.assertEqual(MockRequestCounter.mock_page_requests, 0)

    def test_get_vide_code__watch_more_args(self):
        MockRequestCounter.mock_page_requests = 0

        handler = YouTubeVideoHandler("https://www.youtube.com/watch?app=desktop&v=nkll0StZJLA&t=34s")
        self.assertEqual(handler.get_video_code(), "nkll0StZJLA")

        self.assertEqual(MockRequestCounter.mock_page_requests, 0)

    def test_get_video_code__with_time(self):
        MockRequestCounter.mock_page_requests = 0

        handler = YouTubeVideoHandler(
            "https://www.youtube.com/watch?v=uN_ab1GTXvY&t=50s"
        )
        self.assertEqual(handler.get_video_code(), "uN_ab1GTXvY")

        self.assertEqual(MockRequestCounter.mock_page_requests, 0)

    def test_get_video_code__with_time_first(self):
        MockRequestCounter.mock_page_requests = 0

        handler = YouTubeVideoHandler(
            "https://www.youtube.com/watch?t=50s&v=uN_ab1GTXvY"
        )
        self.assertEqual(handler.get_video_code(), "uN_ab1GTXvY")

        self.assertEqual(MockRequestCounter.mock_page_requests, 0)

    def test_get_video_code__youtube(self):
        MockRequestCounter.mock_page_requests = 0

        handler = YouTubeVideoHandler("https://youtu.be/1234")
        self.assertEqual(handler.get_video_code(), "1234")

        self.assertEqual(MockRequestCounter.mock_page_requests, 0)

    def test_get_video_code__youtube_time(self):
        handler = YouTubeVideoHandler("https://www.youtu.be/1234?t=50")
        self.assertEqual(handler.get_video_code(), "1234")

    def test_code2url(self):
        MockRequestCounter.mock_page_requests = 0

        self.assertEqual(
            YouTubeVideoHandler("1234").code2url("1234"),
            "https://www.youtube.com/watch?v=1234",
        )

        self.assertEqual(MockRequestCounter.mock_page_requests, 0)

    def test_get_link_embed(self):
        MockRequestCounter.mock_page_requests = 0
        test_link = "https://www.youtube.com/watch?v=123"

        handler = YouTubeJsonHandlerMock(test_link, url_builder=Url)

        # call tested function
        link_embed = handler.get_link_embed()
        self.assertEqual(link_embed, "https://www.youtube.com/embed/123")
        self.assertEqual(MockRequestCounter.mock_page_requests, 0)

    def test_get_response(self):
        MockRequestCounter.mock_page_requests = 0
        test_link = "https://www.youtube.com/watch?v=123"

        handler = YouTubeJsonHandlerMock(test_link, url_builder=Url)

        # call tested function
        response = handler.get_response()

        self.assertTrue(response)
        self.assertEqual(MockRequestCounter.mock_page_requests, 1)

    def test_get_contents_hash(self):
        MockRequestCounter.mock_page_requests = 0
        test_link = "https://www.youtube.com/watch?v=123"

        handler = YouTubeJsonHandlerMock(test_link, url_builder=Url)

        # call tested function
        hash = handler.get_contents_hash()

        self.assertTrue(hash)
        self.assertEqual(MockRequestCounter.mock_page_requests, 1)

    def test_get_contents_body_hash(self):
        MockRequestCounter.mock_page_requests = 0
        test_link = "https://www.youtube.com/watch?v=123"

        handler = YouTubeJsonHandlerMock(test_link, url_builder=Url)

        # call tested function
        hash = handler.get_contents_body_hash()

        self.assertTrue(hash)

    def test_get_contents(self):
        MockRequestCounter.mock_page_requests = 0
        test_link = "https://www.youtube.com/watch?v=123"

        handler = YouTubeJsonHandlerMock(test_link, url_builder=Url)

        # call tested function
        contents = handler.get_contents()

        self.assertTrue(contents)
        self.assertEqual(MockRequestCounter.mock_page_requests, 1)

    def test_get_response(self):
        MockRequestCounter.mock_page_requests = 0
        test_link = "https://www.youtube.com/watch?v=123"

        handler = YouTubeJsonHandlerMock(test_link, url_builder=Url)

        # call tested function
        response = handler.get_response()

        self.assertTrue(response)
        self.assertEqual(MockRequestCounter.mock_page_requests, 1)

    def test_get_date_published(self):
        MockRequestCounter.mock_page_requests = 0
        test_link = "https://www.youtube.com/watch?v=archived"

        handler = YouTubeJsonHandlerMock(test_link, url_builder=Url)

        response = handler.get_response()
        # call tested function
        date = handler.get_date_published()

        expected_date_published = DateUtils.from_string("2023-11-13;00:00", "%Y-%m-%d;%H:%M")
        expected_date_published = DateUtils.to_utc_date(expected_date_published)

        self.assertEqual(date, expected_date_published)
        self.assertEqual(MockRequestCounter.mock_page_requests, 1)


class YouTubeChannelHandlerTest(FakeInternetTestCase):
    def setUp(self):
        self.disable_web_pages()

    def test_constructor__rss(self):
        MockRequestCounter.mock_page_requests = 0

        # call tested function
        handler = YouTubeChannelHandler(
            "https://www.youtube.com/feeds/videos.xml?channel_id=SAMTIMESAMTIMESAMTIMESAM",
            url_builder=Url
        )

        self.assertEqual(
            handler.get_feeds()[0],
            "https://www.youtube.com/feeds/videos.xml?channel_id=SAMTIMESAMTIMESAMTIMESAM",
        )

        self.assertEqual(MockRequestCounter.mock_page_requests, 0)

    def test_constructor__channel(self):
        MockRequestCounter.mock_page_requests = 0

        test_link = "https://www.youtube.com/channel/1234"
        # call tested function
        handler = YouTubeChannelHandler(test_link, url_builder=Url)
        self.assertEqual(handler.url, test_link)

        self.assertEqual(MockRequestCounter.mock_page_requests, 0)

    def test_constructor__user(self):
        MockRequestCounter.mock_page_requests = 0

        test_link = "https://www.youtube.com/user/1234"
        # call tested function
        handler = YouTubeChannelHandler(test_link, url_builder=Url)
        self.assertEqual(handler.url, test_link)

        # +1 - obtains channel code from HTML
        self.assertEqual(MockRequestCounter.mock_page_requests, 0)

    def test_is_handled_by__channel(self):
        MockRequestCounter.mock_page_requests = 0

        test_link = "https://www.youtube.com/channel/1234"
        # call tested function
        handler = YouTubeChannelHandler(test_link, url_builder=Url)
        self.assertTrue(handler.is_handled_by())

    def test_is_handled_by__user(self):
        MockRequestCounter.mock_page_requests = 0

        test_link = "https://www.youtube.com/user/1234"
        # call tested function
        handler = YouTubeChannelHandler(test_link, url_builder=Url)
        self.assertTrue(handler.is_handled_by())

    def test_is_handled_by__feed(self):
        MockRequestCounter.mock_page_requests = 0

        test_link = "https://www.youtube.com/feeds/videos.xml?channel_id=SAMTIMESAMTIMESAMTIMESAM"

        # call tested function
        handler = YouTubeChannelHandler(test_link, url_builder=Url)
        self.assertTrue(handler.is_handled_by())

    def test_source_input2code_channel(self):
        MockRequestCounter.mock_page_requests = 0
        self.assertEqual(
            YouTubeChannelHandler(
                "https://www.youtube.com/channel/1234"
            ).get_channel_code(),
            "1234",
        )

        self.assertEqual(MockRequestCounter.mock_page_requests, 0)

    def test_source_input2code_feed(self):
        MockRequestCounter.mock_page_requests = 0

        self.assertEqual(
            YouTubeChannelHandler(
                "https://www.youtube.com/feeds/videos.xml?channel_id=1234"
            ).get_channel_code(),
            "1234",
        )

        self.assertEqual(MockRequestCounter.mock_page_requests, 0)

    def test_source_code2feed(self):
        MockRequestCounter.mock_page_requests = 0

        test_link = "https://www.youtube.com/feeds/videos.xml?channel_id=1234"

        handler = YouTubeChannelHandler(test_link)

        self.assertIn(test_link, handler.get_feeds())

        self.assertEqual(MockRequestCounter.mock_page_requests, 0)

    def test_get_channel_url(self):
        MockRequestCounter.mock_page_requests = 0

        handler = YouTubeChannelHandler(
            "https://www.youtube.com/feeds/videos.xml?channel_id=SAMTIMESAMTIMESAMTIMESAM"
        )

        # call tested function
        channel_name = handler.get_channel_url()

        self.assertEqual(
            channel_name,
            "https://www.youtube.com/channel/SAMTIMESAMTIMESAMTIMESAM",
        )

        self.assertEqual(MockRequestCounter.mock_page_requests, 0)

    def test_get_response(self):
        MockRequestCounter.mock_page_requests = 0

        handler = YouTubeChannelHandler(
            "https://www.youtube.com/feeds/videos.xml?channel_id=SAMTIMESAMTIMESAMTIMESAM",
            url_builder=Url
        )

        # call tested function
        response = handler.get_response()

        self.assertTrue(response)

        self.assertEqual(MockRequestCounter.mock_page_requests, 1)

    def test_get_contents_hash(self):
        MockRequestCounter.mock_page_requests = 0
        handler = YouTubeChannelHandler(
            "https://www.youtube.com/feeds/videos.xml?channel_id=SAMTIMESAMTIMESAMTIMESAM",
            url_builder=Url
        )

        # call tested function
        hash = handler.get_contents_hash()

        self.assertTrue(hash)
        self.assertEqual(MockRequestCounter.mock_page_requests, 1)

    def test_get_contents_body_hash(self):
        MockRequestCounter.mock_page_requests = 0
        handler = YouTubeChannelHandler(
            "https://www.youtube.com/feeds/videos.xml?channel_id=SAMTIMESAMTIMESAMTIMESAM",
            url_builder=Url
        )

        # call tested function
        hash = handler.get_contents_body_hash()

        self.assertTrue(hash)
        self.assertEqual(MockRequestCounter.mock_page_requests, 1)

    def test_get_contents(self):
        MockRequestCounter.mock_page_requests = 0
        test_link = "https://www.youtube.com/feeds/videos.xml?channel_id=SAMTIMESAMTIMESAMTIMESAM"

        handler = YouTubeChannelHandler(
            test_link,
            url_builder=Url
        )

        # call tested function
        contents = handler.get_contents()

        self.assertTrue(contents)
        self.assertEqual(MockRequestCounter.mock_page_requests, 1)

    def test_get_response(self):
        MockRequestCounter.mock_page_requests = 0
        test_link = "https://www.youtube.com/feeds/videos.xml?channel_id=SAMTIMESAMTIMESAMTIMESAM"

        handler = YouTubeChannelHandler(
            test_link,
            url_builder=Url
        )

        # call tested function
        response = handler.get_response()

        self.assertTrue(response)
        self.assertEqual(MockRequestCounter.mock_page_requests, 1)

    def test_get_feeds__from_rss(self):
        MockRequestCounter.mock_page_requests = 0

        handler = YouTubeChannelHandler(
            "https://www.youtube.com/feeds/videos.xml?channel_id=SAMTIMESAMTIMESAMTIMESAM"
        )

        # call tested function
        feeds = handler.get_feeds()

        self.assertEqual(len(feeds), 1)
        self.assertEqual(feeds[0], "https://www.youtube.com/feeds/videos.xml?channel_id=SAMTIMESAMTIMESAMTIMESAM")

        self.assertEqual(MockRequestCounter.mock_page_requests, 0)

    def test_get_feeds__from_channel(self):
        MockRequestCounter.mock_page_requests = 0

        handler = YouTubeChannelHandler(
            "https://www.youtube.com/channel/SAMTIMESAMTIMESAMTIMESAM"
        )

        # call tested function
        feeds = handler.get_feeds()

        self.assertEqual(len(feeds), 1)
        self.assertEqual(feeds[0], "https://www.youtube.com/feeds/videos.xml?channel_id=SAMTIMESAMTIMESAMTIMESAM")

        self.assertEqual(MockRequestCounter.mock_page_requests, 0)

    def test_constructor__get_thumbnail(self):
        MockRequestCounter.mock_page_requests = 0

        test_link = "https://www.youtube.com/channel/1234"
        # call tested function
        handler = YouTubeChannelHandler(test_link, url_builder=Url)
        self.assertEqual(handler.url, test_link)

        thumbnail = handler.get_thumbnail()

        # +1 for RSS response +1 for channel HTML response
        self.assertEqual(MockRequestCounter.mock_page_requests, 1)
