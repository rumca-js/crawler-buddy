from webtoolkit import HtmlPage
import requests
import unittest

class TestUrl(unittest.TestCase):
    def test_urlchannel(self):
        test_link = "https://www.youtube.com/channel/UCEES_bv7O-xLNZhTSO4kRUQ"

        cookies = {}
        cookies["CONSENT"] = "YES+cb.20210328-17-p0.en+F+678"

        answer = requests.get(test_link, cookies=cookies)
        answer.text

        page = HtmlPage(test_link, contents = answer.content)
        self.assertTrue(page.get_title())
