from webtoolkit import (
   OdyseeVideoHandler,
   OdyseeChannelHandler,
)

from src.webtools import (
   Url,
)

from tests.fakeinternet import FakeInternetTestCase, MockRequestCounter


class OdyseeVideoHandlerTest(FakeInternetTestCase):
    def setUp(self):
        self.disable_web_pages()

    def test_constructor(self):
        MockRequestCounter.mock_page_requests = 0

        handler = OdyseeVideoHandler(
            "https://odysee.com/@samtime:1/apple-reacts-to-leaked-windows-12:1?test",
            url_builder=Url
        )
        self.assertEqual(
            handler.url,
            "https://odysee.com/@samtime:1/apple-reacts-to-leaked-windows-12:1",
        )

    def test_get_channel_code(self):
        handler = OdyseeVideoHandler(
            "https://odysee.com/@samtime:1/apple-reacts-to-leaked-windows-12:1?test",
            url_builder=Url
        )
        self.assertEqual(handler.get_channel_code(), "@samtime:1")

    def test_is_handled_by__channel_video(self):
        handler = OdyseeVideoHandler(
            "https://odysee.com/@samtime:1/apple-reacts-to-leaked-windows-12:1?test",
            url_builder=Url
        )
        self.assertTrue(handler.is_handled_by())

    def test_is_handled_by__video(self):
        handler = OdyseeVideoHandler(
            "https://odysee.com/ridiculous-zendesk-vulnerability-causes:01c863c36e86789070adf02eaa5c0778975507d5",
            url_builder=Url
        )
        self.assertTrue(handler.is_handled_by())

    def test_get_video_code__channel_video(self):
        handler = OdyseeVideoHandler(
            "https://odysee.com/@samtime:1/apple-reacts-to-leaked-windows-12:1?test",
            url_builder=Url
        )
        code = handler.get_video_code()
        self.assertEqual(code, "apple-reacts-to-leaked-windows-12:1")

    def test_get_video_code__channel_video(self):
        handler = OdyseeVideoHandler(
            "https://odysee.com/ridiculous-zendesk-vulnerability-causes:01c863c36e86789070adf02eaa5c0778975507d5",
            url_builder=Url
        )
        code = handler.get_video_code()
        self.assertEqual(
            code,
            "ridiculous-zendesk-vulnerability-causes:01c863c36e86789070adf02eaa5c0778975507d5",
        )

    def test_get_link_embed(self):
        handler = OdyseeVideoHandler(
            "https://odysee.com/ridiculous-zendesk-vulnerability-causes:01c863c36e86789070adf02eaa5c0778975507d5",
            url_builder=Url
        )
        link_embed = handler.get_link_embed()
        self.assertEqual(
            link_embed,
            "https://odysee.com/$/embed/ridiculous-zendesk-vulnerability-causes:01c863c36e86789070adf02eaa5c0778975507d5",
        )

    def test_get_contents_hash(self):
        test_link = "https://odysee.com/ridiculous-zendesk-vulnerability-causes:01c863c36e86789070adf02eaa5c0778975507d5"
        request = Url(test_link).get_init_request()

        handler = OdyseeVideoHandler(test_link, request=request, url_builder=Url)

        handler.get_response()

        # call tested function
        hash = handler.get_contents_hash()

        self.assertTrue(hash)

    def test_get_contents_body_hash(self):
        test_link = "https://odysee.com/ridiculous-zendesk-vulnerability-causes:01c863c36e86789070adf02eaa5c0778975507d5"
        request = Url(test_link).get_init_request()

        handler = OdyseeVideoHandler(test_link, request=request, url_builder=Url)

        handler.get_response()

        # call tested function
        hash = handler.get_contents_body_hash()

        self.assertTrue(hash)

    def test_get_response(self):
        test_link = "https://odysee.com/ridiculous-zendesk-vulnerability-causes:01c863c36e86789070adf02eaa5c0778975507d5"
        request = Url(test_link).get_init_request()

        handler = OdyseeVideoHandler(test_link, request=request, url_builder=Url)

        # call tested function
        response = handler.get_response()

        self.assertTrue(response)


class OdyseeChannelHandlerTest(FakeInternetTestCase):
    def setUp(self):
        self.disable_web_pages()

    def test_constructor__channel_url(self):
        MockRequestCounter.mock_page_requests = 0

        test_link = "https://odysee.com/@samtime:1?test"

        # call tested function
        handler = OdyseeChannelHandler(test_link, url_builder=Url)

        self.assertEqual(handler.url, test_link)
        self.assertEqual(
            handler.code2url(handler.code), "https://odysee.com/@samtime:1"
        )
        self.assertEqual(
            handler.code2feed(handler.code), "https://odysee.com/$/rss/@samtime:1"
        )
        self.assertEqual(MockRequestCounter.mock_page_requests, 0)

    def test_constructor__feed_url(self):
        MockRequestCounter.mock_page_requests = 0

        test_link = "https://odysee.com/$/rss/@samtime:1?test"

        # call tested function
        handler = OdyseeChannelHandler(test_link, url_builder=Url)

        self.assertEqual(handler.url, test_link)
        self.assertEqual(
            handler.code2url(handler.code), "https://odysee.com/@samtime:1"
        )
        self.assertEqual(
            handler.code2feed(handler.code), "https://odysee.com/$/rss/@samtime:1"
        )
        self.assertEqual(MockRequestCounter.mock_page_requests, 0)

    def test_get_feeds__from_rss(self):
        MockRequestCounter.mock_page_requests = 0

        # call tested function
        handler = OdyseeChannelHandler("https://odysee.com/$/rss/@samtime:1?test", url_builder=Url)

        feeds = handler.get_feeds()
        self.assertEqual(len(feeds), 1)

        self.assertEqual(feeds[0], "https://odysee.com/$/rss/@samtime:1")
        self.assertEqual(MockRequestCounter.mock_page_requests, 0)

    def test_get_feeds__from_handle(self):
        MockRequestCounter.mock_page_requests = 0

        # call tested function
        handler = OdyseeChannelHandler("https://odysee.com/@samtime:1", url_builder=Url)

        feeds = handler.get_feeds()
        self.assertEqual(len(feeds), 1)

        self.assertEqual(feeds[0], "https://odysee.com/$/rss/@samtime:1")
        self.assertEqual(MockRequestCounter.mock_page_requests, 0)

    def test_get_channel_url(self):
        MockRequestCounter.mock_page_requests = 0
        self.assertEqual(
            OdyseeChannelHandler("https://odysee.com/$/rss/@samtime:1").get_channel_url(),
            "https://odysee.com/@samtime:1",
        )
        self.assertEqual(MockRequestCounter.mock_page_requests, 0)

    def test_get_contents_hash(self):
        MockRequestCounter.mock_page_requests = 0
        handler = OdyseeChannelHandler("https://odysee.com/@samtime:1?test", url_builder=Url)

        # call tested function
        hash = handler.get_contents_hash()

        self.assertTrue(hash)
        self.assertEqual(MockRequestCounter.mock_page_requests, 2)

    def test_get_contents_body_hash(self):
        MockRequestCounter.mock_page_requests = 0
        handler = OdyseeChannelHandler("https://odysee.com/@samtime:1?test", url_builder=Url)

        # call tested function
        hash = handler.get_contents_body_hash()

        self.assertTrue(hash)
        self.assertEqual(MockRequestCounter.mock_page_requests, 2)

    def test_get_contents(self):
        MockRequestCounter.mock_page_requests = 0
        handler = OdyseeChannelHandler("https://odysee.com/@samtime:1?test", url_builder=Url)

        # call tested function
        contents = handler.get_contents()

        self.assertTrue(contents)
        self.assertEqual(MockRequestCounter.mock_page_requests, 2)

    def test_get_response(self):
        MockRequestCounter.mock_page_requests = 0
        handler = OdyseeChannelHandler("https://odysee.com/@samtime:1?test", url_builder=Url)

        # call tested function
        response = handler.get_response()

        self.assertTrue(response)
        self.assertEqual(MockRequestCounter.mock_page_requests, 2)
