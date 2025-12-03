from datetime import datetime, timedelta

from src import CrawlerContainer
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
           "crawler_name" : "RequestsCrawler",
           },
       "name" : "Request",
   },
]


class CrawlerContainerTest(FakeInternetTestCase):
    def setUp(self):
        self.disable_web_pages()

    def test_crawl(self):
        history = CrawlerContainer()

        self.assertEqual(history.get_size(), 0)

        # call tested function
        crawl_id = history.crawl(crawl_type=CrawlerContainer.CRAWL_TYPE_GET, url="https://youtube.com")

        self.assertEqual(history.get_size(), 1)
        self.assertTrue(crawl_id is not None)

    def test_update__true(self):
        history = CrawlerContainer()

        self.assertEqual(history.get_size(), 0)

        # call tested function
        crawl_id = history.crawl(crawl_type=CrawlerContainer.CRAWL_TYPE_GET, url="https://youtube.com")

        self.assertEqual(history.get_size(), 1)
        self.assertTrue(crawl_id is not None)

        result = history.update(crawl_id=crawl_id, data=data)
        self.assertEqual(history.get_size(), 1)
        self.assertTrue(result)

    def test_update__false(self):
        history = CrawlerContainer()

        self.assertEqual(history.get_size(), 0)

        # call tested function
        crawl_id = history.crawl(crawl_type=CrawlerContainer.CRAWL_TYPE_GET, url="https://youtube.com")

        self.assertEqual(history.get_size(), 1)
        self.assertTrue(crawl_id is not None)

        result = history.update(crawl_id=1000, data=data)
        self.assertEqual(history.get_size(), 1)
        self.assertFalse(result)

    def test_find__true(self):
        history = CrawlerContainer()

        self.assertEqual(history.get_size(), 0)

        # call tested function
        crawl_id = history.crawl(crawl_type=CrawlerContainer.CRAWL_TYPE_GET, url="https://youtube.com")

        self.assertEqual(history.get_size(), 1)
        self.assertTrue(crawl_id is not None)

        find_crawl_id = history.find(url="https://youtube.com")
        self.assertTrue(find_crawl_id is not None)

    def test_find__false(self):
        history = CrawlerContainer()

        self.assertEqual(history.get_size(), 0)

        # call tested function
        crawl_id = history.crawl(crawl_type=CrawlerContainer.CRAWL_TYPE_GET, url="https://youtube.com")

        self.assertEqual(history.get_size(), 1)
        self.assertTrue(crawl_id is not None)

        find_crawl_id = history.find(url="https://youtube.com/1")
        self.assertTrue(find_crawl_id is None)

    def test_get__true(self):
        history = CrawlerContainer()

        self.assertEqual(history.get_size(), 0)

        # call tested function
        crawl_id = history.crawl(crawl_type=CrawlerContainer.CRAWL_TYPE_GET, url="https://youtube.com")

        self.assertEqual(history.get_size(), 1)
        self.assertTrue(crawl_id is not None)

        get_crawl_data = history.get(crawl_id=crawl_id)
        self.assertTrue(get_crawl_data is not None)

    def test_get__false(self):
        history = CrawlerContainer()

        self.assertEqual(history.get_size(), 0)

        # call tested function
        crawl_id = history.crawl(crawl_type=CrawlerContainer.CRAWL_TYPE_GET, url="https://youtube.com")

        self.assertEqual(history.get_size(), 1)
        self.assertTrue(crawl_id is not None)

        get_crawl_data = history.get(crawl_id=1000)
        self.assertTrue(get_crawl_data is None)

    def test_expire(self):
        history = CrawlerContainer()

        self.assertEqual(history.get_size(), 0)

        # call tested function
        crawl_id = history.crawl(crawl_type=CrawlerContainer.CRAWL_TYPE_GET, url="https://youtube.com")

        self.assertEqual(history.get_size(), 1)

        for item in history.container:
            item.timestamp = datetime.now() - timedelta(minutes=10000)

        history.expire_old()

        self.assertEqual(history.get_size(), 0)

    def test_trim(self):
        history = CrawlerContainer(records_size = 3)

        self.assertEqual(history.get_size(), 0)

        # call tested function
        crawl_id = history.crawl(crawl_type=CrawlerContainer.CRAWL_TYPE_GET, url="https://youtube.com/1")
        crawl_id = history.crawl(crawl_type=CrawlerContainer.CRAWL_TYPE_GET, url="https://youtube.com/2")
        crawl_id = history.crawl(crawl_type=CrawlerContainer.CRAWL_TYPE_GET, url="https://youtube.com/3")
        crawl_id = history.crawl(crawl_type=CrawlerContainer.CRAWL_TYPE_GET, url="https://youtube.com/4")
        crawl_id = history.crawl(crawl_type=CrawlerContainer.CRAWL_TYPE_GET, url="https://youtube.com/5")

        self.assertEqual(history.get_size(), 3)
