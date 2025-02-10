from rsshistory.webtools import OpmlPage
from tests.fake.opmlfile import opml_file

from tests.fakeinternet import FakeInternetTestCase, MockRequestCounter


class OmplPageTest(FakeInternetTestCase):

    def test_is_valid(self):
        MockRequestCounter.mock_page_requests = 0

        p = OpmlPage("https://linkedin.com/test", opml_file)

        self.assertTrue(p.is_valid())

    def test_get_entries(self):
        MockRequestCounter.mock_page_requests = 0

        p = OpmlPage("https://linkedin.com/test", opml_file)

        entries = list(p.get_entries())

        self.assertTrue(len(entries) > 0)

        self.assertEqual(MockRequestCounter.mock_page_requests, 0)
