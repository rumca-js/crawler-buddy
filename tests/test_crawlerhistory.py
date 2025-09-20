from src import CrawlerHistory
from tests.fakeinternet import FakeInternetTestCase


data = [
   {
       "data" : {},
       "name" : "Properties",
   },
   {
       "data" : {},
       "name" : "Properties",
   },
   {
       "data" : {},
       "name" : "Text",
   },
   {
       "data" : {},
       "name" : "Streams",
   },
   {
       "data" : {
           "crawler" : "RequestsCrawler",
           "name" : "RequestsCrawler",
           },
       "name" : "Settings",
   },
]


class CrawlerHistoryTest(FakeInternetTestCase):
    def setUp(self):
        self.disable_web_pages()

    def test_add(self):
        history = CrawlerHistory()

        self.assertEqual(history.get_size(), 0)

        # call tested function
        history.add(["https://youtube.com", data])

        self.assertEqual(history.get_size(), 1)

    def test_find__true(self):
        history = CrawlerHistory()

        self.assertEqual(history.get_size(), 0)

        history.add(["https://youtube.com", data])

        # call tested function
        things = history.find(url = "https://youtube.com")

        self.assertTrue(things)

        index, timestamp, props = things
        self.assertEqual(index, 0)

    def test_find__true__by_name(self):
        history = CrawlerHistory()

        self.assertEqual(history.get_size(), 0)

        history.add(["https://youtube.com", data])

        # call tested function
        things = history.find(url = "https://youtube.com", crawler_name="RequestsCrawler")

        self.assertTrue(things)

        index, timestamp, props = things
        self.assertEqual(index, 0)

    def test_find__false(self):
        history = CrawlerHistory()

        self.assertEqual(history.get_size(), 0)

        history.add(["https://youtube.com", data])

        # call tested function
        status = history.find(url = "https://google.com")

        self.assertFalse(status)

    def test_remove(self):
        history = CrawlerHistory()

        self.assertEqual(history.get_size(), 0)
        index = history.add(["https://youtube.com", data])
        self.assertEqual(history.get_size(), 1)

        # call tested function
        history.remove(index)

        self.assertEqual(history.get_size(), 0)
