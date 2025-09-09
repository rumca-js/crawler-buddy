from src import CrawlerHistory
from tests.fakeinternet import FakeInternetTestCase


class CrawlerHistoryTest(FakeInternetTestCase):
    def setUp(self):
        self.disable_web_pages()

    def test_add(self):
        history = CrawlerHistory()

        self.assertEqual(history.get_history_size(), 0)

        # call tested function
        history.add(["https://youtube.com", ""])

        self.assertEqual(history.get_history_size(), 1)

    def test_find__true(self):
        history = CrawlerHistory()

        self.assertEqual(history.get_history_size(), 0)

        history.add(["https://youtube.com", ""])

        # call tested function
        status = history.find(url = "https://youtube.com")

        self.assertTrue(status)

    def test_find__false(self):
        history = CrawlerHistory()

        self.assertEqual(history.get_history_size(), 0)

        history.add(["https://youtube.com", ""])

        # call tested function
        status = history.find(url = "https://google.com")

        self.assertFalse(status)

    def test_remove(self):
        history = CrawlerHistory()

        self.assertEqual(history.get_history_size(), 0)
        index = history.add(["https://youtube.com", ""])
        self.assertEqual(history.get_history_size(), 1)

        # call tested function
        history.remove(index)

        self.assertEqual(history.get_history_size(), 0)
