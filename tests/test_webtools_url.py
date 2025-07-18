from src.webtools import (
    Url,
    PageOptions,
    HtmlPage,
    RssPage,
    PageResponseObject,
    HttpPageHandler,
    RedditUrlHandler,
)

from tests.fakeinternet import FakeInternetTestCase, MockRequestCounter


class UrlTest(FakeInternetTestCase):
    def setUp(self):
        self.disable_web_pages()

    def test_get_cleaned_link(self):
        MockRequestCounter.mock_page_requests = 0

        test_link = "https://my-server:8185/view/somethingsomething/"

        # call tested function
        link = Url.get_cleaned_link(test_link)

        self.assertEqual(link, "https://my-server:8185/view/somethingsomething")

        self.assertEqual(MockRequestCounter.mock_page_requests, 0)

    def test_get_cleaned_link__space(self):
        MockRequestCounter.mock_page_requests = 0

        test_link = " https://my-server:8185/view/somethingsomething/"

        # call tested function
        link = Url.get_cleaned_link(test_link)

        self.assertEqual(link, "https://my-server:8185/view/somethingsomething")
        self.assertEqual(MockRequestCounter.mock_page_requests, 0)

    def test_get_cleaned_link__stupid_google_link(self):
        MockRequestCounter.mock_page_requests = 0

        cleaned_link = Url.get_cleaned_link(
            "https://www.google.com/url?q=https://forum.ddopl.com/&sa=Udupa"
        )

        self.assertEqual(cleaned_link, "https://forum.ddopl.com/")

        self.assertEqual(MockRequestCounter.mock_page_requests, 0)

    def test_get_cleaned_link__stupid_google_link2(self):
        MockRequestCounter.mock_page_requests = 0

        cleaned_link = Url.get_cleaned_link(
            "https://www.google.com/url?sa=t&source=web&rct=j&opi=89978449&url=https://worldofwarcraft.blizzard.com/&ved=2ahUKEwjtx56Pn5WFAxU2DhAIHYR1CckQFnoECCkQAQ&usg=AOvVaw1pDkx5K7B5loKccvg_079-"
        )

        self.assertEqual(cleaned_link, "https://worldofwarcraft.blizzard.com/")

        self.assertEqual(MockRequestCounter.mock_page_requests, 0)

    def test_get_cleaned_link__stupid_youtube_link(self):
        MockRequestCounter.mock_page_requests = 0

        cleaned_link = Url.get_cleaned_link(
            "https://www.youtube.com/redirect?event=lorum&redir_token=ipsum&q=https%3A%2F%2Fcorridordigital.com%2F&v=LeB9DcFT810"
        )

        self.assertEqual(cleaned_link, "https://corridordigital.com")

        self.assertEqual(MockRequestCounter.mock_page_requests, 0)

    def test_get_cleaned_link(self):
        MockRequestCounter.mock_page_requests = 0

        cleaned_link = Url.get_cleaned_link("https://www.YouTube.com/Test")
        self.assertEqual(cleaned_link, "https://www.youtube.com/Test")

        cleaned_link = Url.get_cleaned_link("https://www.YouTube.com/Test/")
        self.assertEqual(cleaned_link, "https://www.youtube.com/Test")

        self.assertEqual(MockRequestCounter.mock_page_requests, 0)

    def test_get_handler_by_name(self):
        MockRequestCounter.mock_page_requests = 0

        # call tested function
        handler = Url.get_handler_by_name("HttpPageHandler")

        self.assertTrue(handler)
        self.assertEqual(handler, HttpPageHandler)

        # call tested function
        handler = Url.get_handler_by_name("YouTubeChannelHandler")

        self.assertTrue(handler)
        self.assertNotEqual(handler, HttpPageHandler)

        self.assertEqual(MockRequestCounter.mock_page_requests, 0)

    def test_get_handler__https_html_page(self):
        MockRequestCounter.mock_page_requests = 0

        url = Url("https://multiple-favicons.com/page.html")
        url.get_response()

        self.assertEqual(type(url.get_handler()), HttpPageHandler)
        # call tested function
        self.assertEqual(type(url.get_handler().p), HtmlPage)

        self.assertEqual(MockRequestCounter.mock_page_requests, 1)

    def test_get_handler__http_html_page(self):
        MockRequestCounter.mock_page_requests = 0

        url = Url("http://multiple-favicons.com/page.html")
        url.get_response()

        self.assertEqual(type(url.get_handler()), HttpPageHandler)
        # call tested function
        self.assertEqual(type(url.get_handler().p), HtmlPage)

        self.assertEqual(MockRequestCounter.mock_page_requests, 1)

    def test_get_handler__reddit(self):
        MockRequestCounter.mock_page_requests = 0

        url = Url("https://www.reddit.com/r/searchengines/.rss")
        url.get_response()

        self.assertEqual(type(url.get_handler()), RedditUrlHandler)
        # call tested function
        self.assertEqual(type(url.get_handler().p), RssPage)

        self.assertEqual(MockRequestCounter.mock_page_requests, 1)

    def test_get_handler__ftp_page(self):
        MockRequestCounter.mock_page_requests = 0

        url = Url("ftp://multiple-favicons.com/page.html")

        expected_error = False
        try:
            url.get_response()
        except NotImplementedError as E:
            expected_error = True

        self.assertTrue(expected_error)
        # self.assertEqual(url.get_handler(), None)

        self.assertEqual(MockRequestCounter.mock_page_requests, 0)

    def test_get_handler__rss_page(self):
        MockRequestCounter.mock_page_requests = 0

        # call tested function
        url = Url("https://www.codeproject.com/WebServices/NewsRSS.aspx")

        handler = url.get_handler()

        self.assertTrue(type(handler), HttpPageHandler)

        self.assertEqual(MockRequestCounter.mock_page_requests, 0)

    def test_get_handler__youtube_channel(self):
        MockRequestCounter.mock_page_requests = 0

        # call tested function
        url = Url(
            "https://www.youtube.com/feeds/videos.xml?channel_id=UCXuqSBlHAE6Xw-yeJA0Tunw"
        )

        handler = url.get_handler()

        self.assertTrue(type(handler), Url.youtube_channel_handler)

        self.assertEqual(MockRequestCounter.mock_page_requests, 0)

    def test_get_handler__youtube_video(self):
        MockRequestCounter.mock_page_requests = 0

        # call tested function
        url = Url("https://www.youtube.com/watch?v=1234")

        handler = url.get_handler()

        self.assertTrue(type(handler), Url.youtube_video_handler)

        self.assertEqual(MockRequestCounter.mock_page_requests, 0)

    def test_get_handler__https_html_page__norequest(self):
        MockRequestCounter.mock_page_requests = 0

        url = Url("https://multiple-favicons.com/page.html")

        # call tested function

        self.assertEqual(type(url.get_handler()), HttpPageHandler)
        self.assertEqual(url.get_handler().p, None)

        self.assertEqual(MockRequestCounter.mock_page_requests, 0)

    def test_get_type__html_page(self):
        MockRequestCounter.mock_page_requests = 0

        handler = Url.get_type("https://multiple-favicons.com/page.html")

        # call tested function
        self.assertEqual(type(handler), HtmlPage)

        self.assertEqual(MockRequestCounter.mock_page_requests, 0)

    def test_get_handler__rss_page(self):
        MockRequestCounter.mock_page_requests = 0

        # call tested function
        handler = Url.get_type("https://www.codeproject.com/WebServices/NewsRSS.aspx")

        self.assertTrue(type(handler), HtmlPage)

        self.assertEqual(MockRequestCounter.mock_page_requests, 0)

    def test_get_handler__youtube_channel(self):
        MockRequestCounter.mock_page_requests = 0

        # call tested function
        handler = Url.get_type(
            "https://www.youtube.com/feeds/videos.xml?channel_id=UCXuqSBlHAE6Xw-yeJA0Tunw"
        )

        self.assertTrue(type(handler), Url.youtube_channel_handler)

    def test_get_handler__youtube_video(self):
        MockRequestCounter.mock_page_requests = 0

        # call tested function
        handler = Url.get_type("https://www.youtube.com/watch?v=1234")

        self.assertTrue(type(handler), Url.youtube_video_handler)

        self.assertEqual(MockRequestCounter.mock_page_requests, 0)

    def test_get_properties__rss__basic(self):
        MockRequestCounter.mock_page_requests = 0

        test_link = "https://www.codeproject.com/WebServices/NewsRSS.aspx"

        # call tested function
        url = Url(test_link)

        url.get_response()
        properties = url.get_properties()

        self.assertTrue("title" in properties)
        self.assertTrue("link" in properties)

        self.assertEqual(properties["link"], test_link)
        self.assertEqual(properties["link_request"], test_link)

        self.assertEqual(MockRequestCounter.mock_page_requests, 1)

    def test_get_properties__youtube_channel__basic(self):
        MockRequestCounter.mock_page_requests = 0

        test_link = "https://www.youtube.com/feeds/videos.xml?channel_id=UCXuqSBlHAE6Xw-yeJA0Tunw"
        channel_link = "https://www.youtube.com/channel/UCXuqSBlHAE6Xw-yeJA0Tunw"

        # call tested function
        url = Url(test_link)

        url.get_response()
        properties = url.get_properties()

        self.assertTrue("title" in properties)
        self.assertTrue("link" in properties)

        self.assertEqual(properties["link"], test_link)
        self.assertEqual(properties["link_request"], test_link)

        self.assertEqual(MockRequestCounter.mock_page_requests, 1)

    def test_get_properties__youtube_video__basic(self):
        MockRequestCounter.mock_page_requests = 0

        test_link = "https://www.youtube.com/watch?v=1234"

        # call tested function
        url = Url(test_link)

        url.get_response()
        properties = url.get_properties()

        self.assertTrue("title" in properties)
        self.assertTrue("link" in properties)

        self.assertEqual(properties["link"], test_link)
        self.assertEqual(properties["link_request"], test_link)

        self.assertEqual(MockRequestCounter.mock_page_requests, 1)

    def test_get_properties__html__basic(self):
        MockRequestCounter.mock_page_requests = 0

        test_link = "https://page-with-two-links.com"

        # call tested function
        url = Url(test_link)

        url.get_response()
        properties = url.get_properties()

        self.assertTrue("title" in properties)
        self.assertTrue("link" in properties)

        self.assertEqual(properties["link"], test_link)
        self.assertEqual(properties["link_request"], test_link)

        self.assertEqual(MockRequestCounter.mock_page_requests, 1)

    def test_get_properties__html__advanced(self):
        MockRequestCounter.mock_page_requests = 0

        test_link = "https://page-with-two-links.com"

        # call tested function
        url = Url(test_link)

        url.get_response()
        all_properties = url.get_properties(full=True)

        self.assertTrue(len(all_properties) > 0)
        self.assertEqual(all_properties[0]["name"], "Properties")

        properties = all_properties[0]["data"]

        self.assertIn("title", properties)
        self.assertIn("link", properties)

        self.assertEqual(properties["link"], test_link)
        self.assertEqual(properties["link_request"], test_link)

        self.assertEqual(MockRequestCounter.mock_page_requests, 1)

    def test_get_properties__rss__advanced(self):
        MockRequestCounter.mock_page_requests = 0

        test_link = "https://www.codeproject.com/WebServices/NewsRSS.aspx"

        # call tested function
        url = Url(test_link)

        url.get_response()
        all_properties = url.get_properties(full=True)

        self.assertTrue(len(all_properties) > 0)
        self.assertEqual(all_properties[0]["name"], "Properties")

        properties = all_properties[0]["data"]

        self.assertIn("title", properties)
        self.assertIn("link", properties)
        self.assertIn("feeds", properties)

        self.assertEqual(properties["link"], test_link)
        self.assertEqual(properties["link_request"], test_link)

        self.assertEqual(all_properties[5]["name"], "Entries")
        entries = all_properties[5]["data"]
        self.assertTrue(len(entries) > 0)

        self.assertEqual(MockRequestCounter.mock_page_requests, 1)

    def test_get_properties__youtube_channel__advanced(self):
        MockRequestCounter.mock_page_requests = 0

        test_link = "https://www.youtube.com/feeds/videos.xml?channel_id=UCXuqSBlHAE6Xw-yeJA0Tunw"
        channel_link = "https://www.youtube.com/channel/UCXuqSBlHAE6Xw-yeJA0Tunw"

        # call tested function
        url = Url(test_link)

        url.get_response()
        all_properties = url.get_properties(full=True)

        self.assertTrue(len(all_properties) > 0)
        self.assertEqual(all_properties[0]["name"], "Properties")

        properties = all_properties[0]["data"]

        self.assertIn("title", properties)
        self.assertIn("link", properties)
        self.assertIn("feeds", properties)

        self.assertEqual(properties["link"], test_link)
        self.assertEqual(properties["link_request"], test_link)

        self.assertEqual(all_properties[5]["name"], "Entries")
        entries = all_properties[5]["data"]
        self.assertTrue(len(entries) > 0)

        self.assertEqual(MockRequestCounter.mock_page_requests, 1)

    def test_get_properties__odysee_channel__advanced(self):
        MockRequestCounter.mock_page_requests = 0

        test_link = "https://odysee.com/$/rss/@DistroTube:2"

        # call tested function
        url = Url(test_link)

        url.get_response()
        all_properties = url.get_properties(full=True)

        self.assertTrue(len(all_properties) > 0)
        self.assertEqual(all_properties[0]["name"], "Properties")

        properties = all_properties[0]["data"]

        self.assertIn("title", properties)
        self.assertIn("link", properties)
        self.assertIn("feeds", properties)

        #self.assertEqual(properties["link"], test_link)
        self.assertEqual(properties["link_request"], test_link)

        self.assertEqual(all_properties[5]["name"], "Entries")
        entries = all_properties[5]["data"]
        self.assertTrue(len(entries) > 0)

        self.assertEqual(MockRequestCounter.mock_page_requests, 2)

    def test_get_properties__youtube_video__advanced(self):
        MockRequestCounter.mock_page_requests = 0

        test_link = "https://www.youtube.com/watch?v=1234"

        # call tested function
        url = Url(test_link)

        url.get_response()
        all_properties = url.get_properties(full=True)

        self.assertTrue(len(all_properties) > 0)
        self.assertEqual(all_properties[0]["name"], "Properties")

        properties = all_properties[0]["data"]

        self.assertIn("title", properties)
        self.assertIn("link", properties)
        self.assertIn("feeds", properties)

        self.assertEqual(properties["link"], test_link)
        self.assertEqual(properties["link_request"], test_link)

        self.assertEqual(MockRequestCounter.mock_page_requests, 1)

    def test_get_properties__image_advanced(self):
        MockRequestCounter.mock_page_requests = 0

        test_link = "https://binary.jpg.com"

        # call tested function
        url = Url(test_link)

        url.get_response()
        all_properties = url.get_properties(full=True)

        self.assertTrue(len(all_properties) > 0)
        self.assertEqual(all_properties[0]["name"], "Properties")

        properties = all_properties[0]["data"]

        self.assertIn("title", properties)
        self.assertIn("link", properties)

        self.assertEqual(properties["link"], test_link)
        self.assertEqual(properties["link_request"], test_link)

        self.assertTrue(len(all_properties) > 0)
        self.assertEqual(all_properties[1]["name"], "Binary")
        self.assertTrue(all_properties[1]["data"]["Contents"])

        self.assertEqual(all_properties[3]["name"], "Response")
        self.assertEqual(all_properties[3]["data"]["Content-Type"], "image/jpg")

        self.assertEqual(MockRequestCounter.mock_page_requests, 1)

    def test_get_properties__audio_advanced(self):
        MockRequestCounter.mock_page_requests = 0

        test_link = "https://audio.jpg.com"

        # call tested function
        url = Url(test_link)

        url.get_response()
        all_properties = url.get_properties(full=True)

        self.assertTrue(len(all_properties) > 0)
        self.assertEqual(all_properties[0]["name"], "Properties")

        properties = all_properties[0]["data"]

        self.assertIn("title", properties)
        self.assertIn("link", properties)

        self.assertEqual(properties["link"], test_link)
        self.assertEqual(properties["link_request"], test_link)

        self.assertTrue(len(all_properties) > 0)
        self.assertEqual(all_properties[1]["name"], "Binary")
        self.assertTrue(all_properties[1]["data"]["Contents"])

        self.assertEqual(all_properties[3]["name"], "Response")
        self.assertEqual(all_properties[3]["data"]["Content-Type"], "audio/midi")

        self.assertEqual(MockRequestCounter.mock_page_requests, 1)

    def test_get_properties__video_advanced(self):
        MockRequestCounter.mock_page_requests = 0

        test_link = "https://video.jpg.com"

        # call tested function
        url = Url(test_link)

        url.get_response()
        all_properties = url.get_properties(full=True)

        self.assertTrue(len(all_properties) > 0)
        self.assertEqual(all_properties[0]["name"], "Properties")

        properties = all_properties[0]["data"]

        self.assertIn("title", properties)
        self.assertIn("link", properties)

        self.assertEqual(properties["link"], test_link)
        self.assertEqual(properties["link_request"], test_link)

        self.assertTrue(len(all_properties) > 0)
        self.assertEqual(all_properties[1]["name"], "Binary")
        self.assertTrue(all_properties[1]["data"]["Contents"])

        self.assertEqual(all_properties[3]["name"], "Response")
        self.assertEqual(all_properties[3]["data"]["Content-Type"], "video/mp4")

        self.assertEqual(MockRequestCounter.mock_page_requests, 1)

    def test_get_contents__pass(self):
        url = Url("https://multiple-favicons.com/page.html")
        # call tested function
        contents = url.get_contents()
        self.assertTrue(contents != None)

    def test_get_robots_txt_url(self):
        url = Url("https://page-with-http-status-500.com")
        # call tested function
        robots = url.get_robots_txt_url()
        self.assertEqual(robots, "https://page-with-http-status-500.com/robots.txt")

    def test_get_contents__fails(self):
        MockRequestCounter.reset()

        url = Url("https://page-with-http-status-500.com")

        # call tested function
        contents = url.get_contents()
        self.assertFalse(url.is_valid())

        # 1 for requests +1 for next
        self.assertEqual(MockRequestCounter.mock_page_requests, 1)

        self.assertEqual(len(MockRequestCounter.request_history), 1)

        self.assertEqual(MockRequestCounter.request_history[0]["url"], "https://page-with-http-status-500.com")

    def test_is_valid__html(self):
        MockRequestCounter.mock_page_requests = 0
        url = Url("https://multiple-favicons.com/page.html")

        self.assertEqual(url.get_handler().p, None)

        url.get_response()

        self.assertEqual(type(url.get_handler().p), HtmlPage)

        # call tested function
        self.assertTrue(url.is_valid())

        self.assertEqual(MockRequestCounter.mock_page_requests, 1)

    def test_is_valid__image(self):
        MockRequestCounter.mock_page_requests = 0

        test_link = "https://binary.jpg.com"

        url = Url(test_link)
        url.get_response()

        # call tested function
        self.assertTrue(url.is_valid())

        self.assertEqual(MockRequestCounter.mock_page_requests, 1)

    def test_is_valid__false_response_invalid(self):
        MockRequestCounter.mock_page_requests = 0

        link = "https://multiple-favicons.com/page.html"
        url = Url(link)

        self.assertEqual(type(url.get_handler()), HttpPageHandler)

        self.assertEqual(url.get_handler().p, None)
        url.get_response()

        self.assertEqual(type(url.get_handler().p), HtmlPage)

        url.response = PageResponseObject(link, None, status_code=500)

        # call tested function
        self.assertFalse(url.is_valid())

        self.assertEqual(MockRequestCounter.mock_page_requests, 1)

    def test_get_favicon(self):
        MockRequestCounter.mock_page_requests = 0
        favicon = Url("https://multiple-favicons.com/page.html").get_favicon()

        self.assertEqual(
            favicon, "https://www.youtube.com/s/desktop/e4d15d2c/img/favicon.ico"
        )

        self.assertEqual(MockRequestCounter.mock_page_requests, 1)

    def test_get_last_modified(self):
        MockRequestCounter.mock_page_requests = 0

        handler = Url("https://page-with-last-modified-header.com")

        response = handler.get_response()

        self.assertTrue(response)

        last_modified = response.get_last_modified()
        self.assertTrue(last_modified)

        self.assertEqual(MockRequestCounter.mock_page_requests, 1)

    def test_cache_info__is_allowed(self):
        MockRequestCounter.mock_page_requests = 0

        # call tested function
        handler = Url("https://robots-txt.com/page.html")

        domain_info = handler.get_domain_info()
        self.assertTrue(domain_info)
        self.assertEqual(domain_info.url, "https://robots-txt.com")
        self.assertTrue(domain_info.is_allowed("https://robots-txt.com/any"))
        self.assertFalse(domain_info.is_allowed("https://robots-txt.com/admin/"))
        self.assertTrue(domain_info.is_allowed("https://robots-txt.com/admin"))

    def test_find_rss_url__youtube(self):
        MockRequestCounter.mock_page_requests = 0

        test_link = "https://www.youtube.com/feeds/videos.xml?channel_id=UCXuqSBlHAE6Xw-yeJA0Tunw"

        url = Url(test_link)

        result = Url.find_rss_url(url)
        self.assertEqual(result.url, url.get_feeds()[0])

        self.assertEqual(MockRequestCounter.mock_page_requests, 0)

    def test_get_feeds__youtube_channel(self):
        MockRequestCounter.mock_page_requests = 0

        test_link = "https://www.youtube.com/channel/UCXuqSBlHAE6Xw-yeJA0Tunw"
        test_link_result = "https://www.youtube.com/feeds/videos.xml?channel_id=UCXuqSBlHAE6Xw-yeJA0Tunw"
        url = Url(test_link)

        feeds = url.get_feeds()
        self.assertIn(test_link_result, feeds)
        self.assertEqual(MockRequestCounter.mock_page_requests, 0)

    def test_get_feeds__odysee(self):
        MockRequestCounter.mock_page_requests = 0
        test_link = "https://odysee.com/@samtime:1?test"
        test_link_result = "https://odysee.com/$/rss/@samtime:1"
        url = Url(test_link)

        feeds = url.get_feeds()
        self.assertIn(test_link_result, feeds)
        self.assertEqual(MockRequestCounter.mock_page_requests, 0)

    def test_get_feeds__rss(self):
        MockRequestCounter.mock_page_requests = 0
        test_link = "https://www.codeproject.com/WebServices/NewsRSS.aspx"

        url = Url(test_link)
        url.get_response()

        feeds = url.get_feeds()
        self.assertIn(test_link, feeds)
        self.assertEqual(MockRequestCounter.mock_page_requests, 1)

    def test_get_feeds__opml(self):
        MockRequestCounter.mock_page_requests = 0
        test_link = "https://opml-file-example.com/ompl.xml"
        test_link_result = "https://www.opmllink1.com"

        url = Url(test_link)
        url.get_response()

        feeds = url.get_feeds()
        self.assertIn(test_link_result, feeds)
        self.assertNotIn(test_link, feeds)
        self.assertEqual(MockRequestCounter.mock_page_requests, 1)

    def test_find_rss_url__youtube_channel(self):
        MockRequestCounter.mock_page_requests = 0

        test_link = "https://www.youtube.com/channel/UCXuqSBlHAE6Xw-yeJA0Tunw"
        url = Url(test_link)

        result = Url.find_rss_url(url)
        self.assertEqual(
            result.url,
            "https://www.youtube.com/feeds/videos.xml?channel_id=UCXuqSBlHAE6Xw-yeJA0Tunw",
        )
        self.assertEqual(MockRequestCounter.mock_page_requests, 0)

    def test_find_rss_url__odysee(self):
        MockRequestCounter.mock_page_requests = 0
        url = Url("https://odysee.com/@samtime:1?test")

        result = Url.find_rss_url(url)
        self.assertEqual(result.url, "https://odysee.com/$/rss/@samtime:1")
        self.assertEqual(MockRequestCounter.mock_page_requests, 0)

    def test_find_rss_url__rss(self):
        MockRequestCounter.mock_page_requests = 0
        url = Url("https://www.codeproject.com/WebServices/NewsRSS.aspx")

        result = Url.find_rss_url(url)
        self.assertEqual(result, url)
        self.assertEqual(MockRequestCounter.mock_page_requests, 1)

    def test_get_init_settings__yahoo(self):
        MockRequestCounter.mock_page_requests = 0

        settings = Url("https://yahoo.com/test_link").get_init_settings()

        self.assertIn("name", settings)
        self.assertIn("crawler", settings)
        self.assertIn("settings", settings)

        self.assertEqual(settings["name"], "DefaultCrawler")

        self.assertEqual(MockRequestCounter.mock_page_requests, 0)

    def test_get_init_settings__techcrunch(self):
        MockRequestCounter.mock_page_requests = 0

        settings = Url("https://techcrunch.com/test_link").get_init_settings()

        self.assertIn("name", settings)
        self.assertIn("crawler", settings)
        self.assertIn("settings", settings)

        self.assertEqual(settings["name"], "DefaultCrawler")

        self.assertEqual(MockRequestCounter.mock_page_requests, 0)

    def test_get_contents_hash__html(self):
        MockRequestCounter.mock_page_requests = 0

        url = Url("https://linkedin.com")
        url.get_response()

        # call tested function
        hash = url.get_contents_hash()

        self.assertTrue(hash)

        self.assertEqual(MockRequestCounter.mock_page_requests, 1)

    def test_get_contents_hash__rss(self):
        MockRequestCounter.mock_page_requests = 0

        url = Url("https://www.reddit.com/r/searchengines/.rss")
        url.get_response()

        # call tested function
        hash = url.get_contents_hash()

        self.assertTrue(hash)

        self.assertEqual(MockRequestCounter.mock_page_requests, 1)

    def test_get_contents_hash__youtube_video(self):
        MockRequestCounter.mock_page_requests = 0

        url = Url("https://www.youtube.com/watch?v=1234")
        url.get_response()

        # call tested function
        hash = url.get_contents_hash()

        self.assertTrue(hash)

    def test_get_contents_hash__youtube_channel(self):
        MockRequestCounter.mock_page_requests = 0

        url = Url("https://www.youtube.com/feeds/videos.xml?channel_id=UCXuqSBlHAE6Xw-yeJA0Tunw")
        url.get_response()

        # call tested function
        hash = url.get_contents_hash()

        self.assertTrue(hash)

        self.assertEqual(MockRequestCounter.mock_page_requests, 1)

    def test_get_contents_body_hash__html(self):
        MockRequestCounter.mock_page_requests = 0

        url = Url("https://linkedin.com")
        url.get_response()

        # call tested function
        hash = url.get_contents_body_hash()

        self.assertTrue(hash)

        main_hash = url.get_contents_hash()

        print(url.get_contents())

        self.assertTrue(hash != main_hash)

        self.assertEqual(MockRequestCounter.mock_page_requests, 1)

    def test_get_contents_body_hash__rss(self):
        MockRequestCounter.mock_page_requests = 0

        url = Url("https://www.reddit.com/r/searchengines/.rss")
        url.get_response()

        # call tested function
        hash = url.get_contents_body_hash()

        self.assertTrue(hash)

        main_hash = url.get_contents_hash()

        # print(url.get_contents())

        self.assertTrue(hash != main_hash)

        self.assertEqual(MockRequestCounter.mock_page_requests, 1)

    def test_get_urls__html__canonical(self):
        MockRequestCounter.mock_page_requests = 0

        test_link = "https://page-with-canonical-link.com"
        test_canonical_link = "https://www.page-with-canonical-link.com"

        url = Url(test_link)

        # call tested function
        urls = url.get_urls()

        self.assertEqual(len(urls), 3)
        self.assertEqual(urls["link"], test_link)
        self.assertEqual(urls["link_request"], test_link)
        self.assertEqual(urls["link_canonical"], test_canonical_link)

        self.assertEqual(MockRequestCounter.mock_page_requests, 1)

    def test_get_urls__reddit(self):
        MockRequestCounter.mock_page_requests = 0

        url = Url("https://www.reddit.com/r/searchengines/.rss")

        # call tested function
        urls = url.get_urls()

        self.assertEqual(len(urls), 3)
        self.assertEqual(urls["link"], "https://www.reddit.com/r/searchengines/.rss")
        self.assertEqual(urls["link_request"], "https://www.reddit.com/r/searchengines/.rss")
        self.assertEqual(urls["link_canonical"], "https://www.reddit.com/r/searchengines/.rss")

        self.assertEqual(MockRequestCounter.mock_page_requests, 1)

    def test_get_urls__stupid_link(self):
        MockRequestCounter.mock_page_requests = 0

        test_link = "https://www.youtube.com/redirect?event=lorum&redir_token=ipsum&q=https%3A%2F%2Fcorridordigital.com%2F&v=LeB9DcFT810"

        url = Url(test_link)

        # call tested function
        urls = url.get_urls()

        self.assertEqual(len(urls), 3)
        self.assertEqual(urls["link"], "https://corridordigital.com")
        self.assertEqual(urls["link_request"], "https://www.youtube.com/redirect?event=lorum&redir_token=ipsum&q=https%3A%2F%2Fcorridordigital.com%2F&v=LeB9DcFT810")
        self.assertEqual(urls["link_canonical"], "https://corridordigital.com")

        self.assertEqual(MockRequestCounter.mock_page_requests, 1)

    def test_get_urls__youtube_rss_channel(self):
        MockRequestCounter.mock_page_requests = 0

        test_link = "https://www.youtube.com/feeds/videos.xml?channel_id=UCXuqSBlHAE6Xw-yeJA0Tunw"
        test_channel_link = "https://www.youtube.com/channel/UCXuqSBlHAE6Xw-yeJA0Tunw"

        url = Url(test_link)

        # call tested function
        urls = url.get_urls()

        self.assertEqual(len(urls), 3)
        self.assertEqual(urls["link"], test_link)
        self.assertEqual(urls["link_request"], test_link)
        self.assertEqual(urls["link_canonical"], test_link)

        self.assertEqual(MockRequestCounter.mock_page_requests, 0)

    def test_get_urls__youtube_channel_id(self):
        MockRequestCounter.mock_page_requests = 0

        test_link = "https://www.youtube.com/channel/UCXuqSBlHAE6Xw-yeJA0Tunw"

        url = Url(test_link)

        # call tested function
        urls = url.get_urls()

        self.assertEqual(len(urls), 3)
        self.assertEqual(urls["link"], test_link)
        self.assertEqual(urls["link_request"], test_link)
        self.assertEqual(urls["link_canonical"], test_link)

        self.assertEqual(MockRequestCounter.mock_page_requests, 0)

    def test_get_urls__youtube_channel_id_non_canonical(self):
        MockRequestCounter.mock_page_requests = 0

        test_link = "https://youtube.com/channel/UCXuqSBlHAE6Xw-yeJA0Tunw"
        test_canonical_link = "https://www.youtube.com/channel/UCXuqSBlHAE6Xw-yeJA0Tunw"

        url = Url(test_link)

        # call tested function
        urls = url.get_urls()

        self.assertEqual(len(urls), 3)
        self.assertEqual(urls["link"], test_link)
        self.assertEqual(urls["link_request"], test_link)
        self.assertEqual(urls["link_canonical"], test_canonical_link)

        self.assertEqual(MockRequestCounter.mock_page_requests, 0)

    def test_get_urls__youtube_video(self):
        MockRequestCounter.mock_page_requests = 0

        test_link = "https://www.youtube.com/watch?v=1234"

        url = Url(test_link)

        # call tested function
        urls = url.get_urls()

        self.assertEqual(len(urls), 3)
        self.assertEqual(urls["link"], test_link)
        self.assertEqual(urls["link_request"], test_link)
        self.assertEqual(urls["link_canonical"], test_link)

        self.assertEqual(MockRequestCounter.mock_page_requests, 0)

    def test_get_urls__youtube_video__noncanonical(self):
        MockRequestCounter.mock_page_requests = 0

        test_link = "https://m.youtube.com/watch?v=1234"
        test_canonical_link = "https://www.youtube.com/watch?v=1234"

        url = Url(test_link)

        # call tested function
        urls = url.get_urls()

        self.assertEqual(len(urls), 3)
        self.assertEqual(urls["link"], test_link)
        self.assertEqual(urls["link_request"], test_link)
        self.assertEqual(urls["link_canonical"], test_canonical_link)

        self.assertEqual(MockRequestCounter.mock_page_requests, 0)

    def test_get_social_properties__youtube(self):
        MockRequestCounter.mock_page_requests = 0

        test_link = "https://m.youtube.com/watch?v=1234"

        url = Url(test_link)

        # call tested function
        properties = url.get_social_properties()

        self.assertIn("view_count", properties)
        self.assertTrue(properties["view_count"])

        self.assertIn("thumbs_up", properties)
        self.assertTrue(properties["thumbs_up"])

        self.assertIn("thumbs_down", properties)
        self.assertTrue(properties["thumbs_down"])

        self.assertEqual(MockRequestCounter.mock_page_requests, 1)

    def test_get_social_properties__github(self):
        MockRequestCounter.mock_page_requests = 0

        test_link = "https://github.com/rumca-js?tab=repositories"

        url = Url(test_link)

        # call tested function
        properties = url.get_social_properties()

        self.assertIn("thumbs_up", properties)
        self.assertTrue(properties["thumbs_up"])

        self.assertEqual(MockRequestCounter.mock_page_requests, 1)

    def test_get_social_properties__reddit(self):
        MockRequestCounter.mock_page_requests = 0

        test_link = "https://www.reddit.com/r/redditdev/comments/1hw8p3j/i_used_the_reddit_api_to_save_myself_time_with_my/"

        url = Url(test_link)

        # call tested function
        properties = url.get_social_properties()

        self.assertIn("upvote_ratio", properties)
        self.assertTrue(properties["upvote_ratio"])

        self.assertEqual(MockRequestCounter.mock_page_requests, 1)

    def test_get_social_properties__html(self):
        MockRequestCounter.mock_page_requests = 0

        test_link = "https://linkedin.com/watch?v=1234"

        url = Url(test_link)

        # call tested function
        properties = url.get_social_properties()

        self.assertIn("view_count", properties)
        self.assertIn("thumbs_up", properties)
        self.assertIn("thumbs_down", properties)

        self.assertEqual(MockRequestCounter.mock_page_requests, 0)
