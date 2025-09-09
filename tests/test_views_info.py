

from tests.fakeinternet import FakeInternetTestCase, MockRequestCounter
from script_server import info


class FlaskArgs(object):
    def __init__(self):
        self._map = {}

    def get(self, key):
        if key in self._map:
            return self._map[key]

    def set(self, key, value):
        self._map[key] = value


class FlaskRequest(object):
    def __init__(self, host):
        self.host = host
        self.args = FlaskArgs()

    def set(self, key, value):
        self.args.set(key, value)


class ViewsInfoTest(FakeInternetTestCase):
    def setUp(self):
        self.disable_web_pages()

    def test_info(self):
        request = FlaskRequest("http://192.168.0.0")
        request.set("url", "https://test.com")
        request.set("crawler", "RequestsCrawler")

        #text = info()
        #self.assertTrue(text)
