
from tests.fakeinternet import FakeInternetTestCase, MockRequestCounter, FlaskRequest
from script_server import info



class ViewsInfoTest(FakeInternetTestCase):
    def setUp(self):
        self.disable_web_pages()

    def test_info(self):
        request = FlaskRequest("http://192.168.0.0")
        request.set("url", "https://test.com")
        request.set("crawler", "RequestsCrawler")

        #text = info()
        #self.assertTrue(text)
