from datetime import datetime

from src.views import get_entry_html
from src.webtools import Url
from src.crawlercontainer import CrawlerContainer, CrawlItem

from webtoolkit.tests.fakeinternet import FakeInternetTestCase, MockRequestCounter
from webtoolkit.tests.fakeresponse import FlaskRequest


class ViewsTest(FakeInternetTestCase):
    def setUp(self):
        self.disable_web_pages()

    def test_get_entry_html(self):
        MockRequestCounter.mock_page_requests = 0

        url = Url("https://multiple-favicons.com/page.html")
        url.get_response()
        all_properties = url.get_all_properties()

        crawl_data = CrawlItem(crawl_id=0, crawl_type=CrawlerContainer.CRAWL_TYPE_GET, url="https://example.com")
        crawl_data.data = all_properties

        html = get_entry_html("", crawl_data)
        self.assertTrue(html)
