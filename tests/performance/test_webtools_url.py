import gc

from webtoolkit import (
    HttpPageHandler,
    HtmlPage,
    RssPage,
    PageResponseObject,
    PageRequestObject,
    RedditUrlHandler,
    RemoteServer,
)

from src.webtools import (
    Url,
    YouTubeVideoHandlerJson,
    YouTubeChannelHandlerJson,
)

from utils.memorychecker import MemoryChecker
from src.entryrules import EntryRules
from src.configuration import Configuration

from tests.unit.fakeinternet import FakeInternetTestCase, MockRequestCounter


class UrlMemoryTest(FakeInternetTestCase):
    def setUp(self):
        self.disable_web_pages()
        self.ignore_memory = False

        rules = EntryRules()
        configuration = Configuration()

        self.memory_checker = MemoryChecker()
        self.memory_checker.get_memory_increase()

        self.iteration_count = 500

    def tearDown(self):
        MockRequestCounter.reset()
        gc.collect()

        if not self.ignore_memory:
            memory_increase = self.memory_checker.get_memory_increase()
            self.assertTrue(memory_increase < 20)

    def test_get_response__html(self):
        MockRequestCounter.mock_page_requests = 0

        for i in range(1, self.iteration_count):
            test_link ="https://linkedin.com"
            url = Url(test_link)
            response = url.get_response()
            url.close()

    def test_get_response__rss(self):
        MockRequestCounter.mock_page_requests = 0

        for i in range(1, self.iteration_count):
            test_link = "https://www.codeproject.com/WebServices/NewsRSS.aspx"
            url = Url(test_link)
            response = url.get_response()
            url.close()

    def test_get_response__reddit(self):
        MockRequestCounter.mock_page_requests = 0

        for i in range(1, self.iteration_count):
            test_link = "https://www.reddit.com/r/searchengines/.rss"
            url = Url(test_link)
            response = url.get_response()
            url.close()

    def test_get_response__youtube_channel(self):
        MockRequestCounter.mock_page_requests = 0

        for i in range(1, self.iteration_count):
            test_link = "https://www.youtube.com/feeds/videos.xml?channel_id=UCXuqSBlHAE6Xw-yeJA0Tunw"
            url = Url(test_link)
            response = url.get_response()
            url.close()

    def test_get_response__youtube_video(self):
        MockRequestCounter.mock_page_requests = 0

        for i in range(1, self.iteration_count):
            test_link = "https://www.youtube.com/watch?v=1234"
            url = Url(test_link)
            response = url.get_response()
            url.close()
