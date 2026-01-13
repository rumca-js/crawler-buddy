from datetime import datetime, timedelta

from src import CrawlerContainer
from tests.unit.fakeinternet import FakeInternetTestCase


get_data = [
   {
       "data" : {},
       "name" : "Properties",
   },
   {
       "data" : {},
       "name" : "PropertiesHash",
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

    def test_crawl__get(self):
        history = CrawlerContainer()

        self.assertEqual(history.get_size(), 0)

        # call tested function
        crawl_id = history.crawl(crawl_type=CrawlerContainer.CRAWL_TYPE_GET, url="https://youtube.com")

        self.assertEqual(history.get_size(), 1)
        self.assertTrue(crawl_id is not None)

    def test_crawl__social(self):
        history = CrawlerContainer()

        self.assertEqual(history.get_size(), 0)

        # call tested function
        crawl_id = history.crawl(crawl_type=CrawlerContainer.CRAWL_TYPE_SOCIALDATA, url="https://youtube.com")

        self.assertEqual(history.get_size(), 1)
        self.assertTrue(crawl_id is not None)

    def test_crawl__get_and_social(self):
        history = CrawlerContainer()

        self.assertEqual(history.get_size(), 0)

        # call tested function
        crawl_id1 = history.crawl(crawl_type=CrawlerContainer.CRAWL_TYPE_GET, url="https://youtube.com")
        crawl_id2 = history.crawl(crawl_type=CrawlerContainer.CRAWL_TYPE_SOCIALDATA, url="https://github.com")

        self.assertEqual(history.get_size(), 2)
        self.assertTrue(crawl_id1 is not None)
        self.assertTrue(crawl_id2 is not None)
        self.assertTrue(crawl_id1 != crawl_id2)

    def test_update__true(self):
        history = CrawlerContainer()

        self.assertEqual(history.get_size(), 0)

        crawl_id = history.crawl(crawl_type=CrawlerContainer.CRAWL_TYPE_GET, url="https://youtube.com")

        self.assertEqual(history.get_size(), 1)
        self.assertTrue(crawl_id is not None)

        # call tested function
        result = history.update(crawl_id=crawl_id, data=get_data)
        self.assertEqual(history.get_size(), 1)
        self.assertTrue(result)

    def test_update__false(self):
        history = CrawlerContainer()

        self.assertEqual(history.get_size(), 0)

        crawl_id = history.crawl(crawl_type=CrawlerContainer.CRAWL_TYPE_GET, url="https://youtube.com")

        self.assertEqual(history.get_size(), 1)
        self.assertTrue(crawl_id is not None)

        # call tested function
        result = history.update(crawl_id=1000, data=get_data)
        self.assertEqual(history.get_size(), 1)
        self.assertFalse(result)

    def test_update__two(self):
        history = CrawlerContainer()

        self.assertEqual(history.get_size(), 0)

        crawl_id_get = history.crawl(crawl_type=CrawlerContainer.CRAWL_TYPE_GET, url="https://youtube.com")
        crawl_id_social = history.crawl(crawl_type=CrawlerContainer.CRAWL_TYPE_SOCIALDATA, url="https://github.com")

        self.assertEqual(history.get_size(), 2)
        self.assertTrue(crawl_id_get is not None)
        self.assertTrue(crawl_id_social is not None)

        # call tested function
        result = history.update(crawl_id=crawl_id_get, data=get_data)
        self.assertEqual(history.get_size(), 2)
        self.assertTrue(result)

        crawl_item = history.get(crawl_id=crawl_id_get)
        self.assertTrue(crawl_item)
        self.assertTrue(crawl_item.data)

        crawl_item = history.get(crawl_id=crawl_id_social)
        self.assertTrue(crawl_item)
        self.assertFalse(crawl_item.data)

    def test_find__true(self):
        history = CrawlerContainer()

        self.assertEqual(history.get_size(), 0)

        crawl_id = history.crawl(crawl_type=CrawlerContainer.CRAWL_TYPE_GET, url="https://youtube.com")

        self.assertEqual(history.get_size(), 1)
        self.assertTrue(crawl_id is not None)

        # call tested function
        find_crawl_id = history.find(crawl_type=CrawlerContainer.CRAWL_TYPE_GET, url="https://youtube.com")
        self.assertTrue(find_crawl_id is not None)

    def test_find__false__not_link(self):
        history = CrawlerContainer()

        self.assertEqual(history.get_size(), 0)

        crawl_id = history.crawl(crawl_type=CrawlerContainer.CRAWL_TYPE_GET, url="https://youtube.com")

        self.assertEqual(history.get_size(), 1)
        self.assertTrue(crawl_id is not None)

        # call tested function
        find_crawl_id = history.find(crawl_type=CrawlerContainer.CRAWL_TYPE_GET, url="https://youtube.com/1")
        self.assertTrue(find_crawl_id is None)

    def test_find__false__invalid_type(self):
        history = CrawlerContainer()

        self.assertEqual(history.get_size(), 0)

        crawl_id = history.crawl(crawl_type=CrawlerContainer.CRAWL_TYPE_GET, url="https://youtube.com")

        self.assertEqual(history.get_size(), 1)
        self.assertTrue(crawl_id is not None)

        # call tested function
        find_crawl_id = history.find(crawl_type=CrawlerContainer.CRAWL_TYPE_SOCIALDATA, url="https://youtube.com")
        self.assertTrue(find_crawl_id is None)

    def test_get__by_id_true(self):
        history = CrawlerContainer()

        self.assertEqual(history.get_size(), 0)

        crawl_id = history.crawl(crawl_type=CrawlerContainer.CRAWL_TYPE_GET, url="https://youtube.com")

        self.assertEqual(history.get_size(), 1)
        self.assertTrue(crawl_id is not None)

        # call tested function
        get_crawl_data = history.get(crawl_id=crawl_id)
        self.assertTrue(get_crawl_data is not None)

    def test_get__by_id_false(self):
        history = CrawlerContainer()

        self.assertEqual(history.get_size(), 0)

        crawl_id = history.crawl(crawl_type=CrawlerContainer.CRAWL_TYPE_GET, url="https://youtube.com")

        self.assertEqual(history.get_size(), 1)
        self.assertTrue(crawl_id is not None)

        # call tested function
        get_crawl_data = history.get(crawl_id=1000)
        self.assertTrue(get_crawl_data is None)

    def test_get__two(self):
        history = CrawlerContainer()

        self.assertEqual(history.get_size(), 0)

        crawl_id_get = history.crawl(crawl_type=CrawlerContainer.CRAWL_TYPE_GET, url="https://youtube.com")
        crawl_id_social = history.crawl(crawl_type=CrawlerContainer.CRAWL_TYPE_SOCIALDATA, url="https://github.com")

        self.assertEqual(history.get_size(), 2)
        self.assertTrue(crawl_id_get is not None)
        self.assertTrue(crawl_id_social is not None)

        result = history.update(crawl_id=crawl_id_get, data=get_data)
        self.assertEqual(history.get_size(), 2)
        self.assertTrue(result)

        # call tested function
        crawl_item = history.get(crawl_id=crawl_id_get)
        self.assertTrue(crawl_item)
        self.assertTrue(crawl_item.data)

        # call tested function
        crawl_item = history.get(crawl_id=crawl_id_social)
        self.assertTrue(crawl_item)
        self.assertFalse(crawl_item.data)

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
