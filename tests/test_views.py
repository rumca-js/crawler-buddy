from datetime import datetime

from src.views import get_entry_html
from src.webtools import Url

from tests.fakeinternet import FakeInternetTestCase, MockRequestCounter, FlaskRequest


class ViewsTest(FakeInternetTestCase):
    def setUp(self):
        self.disable_web_pages()

    def test_get_entry_html(self):
        MockRequestCounter.mock_page_requests = 0

        url = Url("https://multiple-favicons.com/page.html")
        url.get_response()
        all_properties = url.get_properties(full=True)

        stamp = datetime.now()

        html = get_entry_html("", 0, "https://example.com", stamp, all_properties)
        self.assertTrue(html)
