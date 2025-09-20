from src import CrawlerQueue
from tests.fakeinternet import FakeInternetTestCase


class CrawlerQueueTest(FakeInternetTestCase):
    def setUp(self):
        self.disable_web_pages()

    def test_add(self):
        history = CrawlerQueue()

        self.assertEqual(history.get_size(), 0)

        # call test function
        index = history.enter("https://youtube.com")

        self.assertEqual(history.get_size(), 1)

    def test_find__true(self):
        history = CrawlerQueue()

        self.assertEqual(history.get_size(), 0)

        index = history.enter("https://youtube.com")

        # call tested function
        status = history.find(input_url = "https://youtube.com")

        self.assertTrue(status)

    def test_find__false(self):
        history = CrawlerQueue()

        self.assertEqual(history.get_size(), 0)

        index = history.enter("https://youtube.com")

        # call tested function
        status = history.find(input_url = "https://google.com")

        self.assertFalse(status)

    def test_leave(self):
        history = CrawlerQueue()

        self.assertEqual(history.get_size(), 0)
        index = history.enter("https://youtube.com")
        self.assertEqual(history.get_size(), 1)

        # call test function
        history.leave(index)

        self.assertEqual(history.get_size(), 0)
