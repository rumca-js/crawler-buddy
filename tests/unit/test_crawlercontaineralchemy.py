from datetime import datetime, timedelta
from pathlib import Path

from webtoolkit import PageRequestObject
from utils.memorychecker import MemoryChecker
from src import CrawlerContainerAlchemy
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


class CrawlerContainerAlchemyTest(FakeInternetTestCase):
    def setUp(self):
        self.disable_web_pages()
        #self.memory_checker = MemoryChecker()
        #self.memory_checker.get_memory_increase()
        self.db_name = "crawlhistorytest.db"
        path = Path(self.db_name)
        if path.exists():
            path.unlink()

    def tearDown(self):
        #memory_increase = self.memory_checker.get_memory_increase()
        #self.assertEqual(memory_increase, 0)
        #print(f"Memory increase: {memory_increase}")
        path = Path(self.db_name)
        if path.exists():
            path.unlink()

    def test_crawl__get(self):
        container = CrawlerContainerAlchemy(db_path=self.db_name)

        self.assertEqual(container.get_size(), 0)

        request = PageRequestObject("https://youtube.com")

        # call tested function
        crawl_id = container.crawl(crawl_type=CrawlerContainer.CRAWL_TYPE_GET, request=request)

        self.assertEqual(container.get_size(), 1)
        self.assertTrue(crawl_id is not None)

    def test_crawl__social(self):
        container = CrawlerContainerAlchemy(db_path=self.db_name)

        self.assertEqual(container.get_size(), 0)
        request = PageRequestObject("https://youtube.com")

        # call tested function
        crawl_id = container.crawl(crawl_type=CrawlerContainer.CRAWL_TYPE_SOCIALDATA, request=request)

        self.assertEqual(container.get_size(), 1)
        self.assertTrue(crawl_id is not None)

    def test_crawl__get_and_social(self):
        container = CrawlerContainerAlchemy(db_path=self.db_name)

        self.assertEqual(container.get_size(), 0)

        request1 = PageRequestObject("https://youtube.com")
        request2 = PageRequestObject("https://github.com")

        # call tested function
        crawl_id1 = container.crawl(crawl_type=CrawlerContainer.CRAWL_TYPE_GET, request=request1)
        crawl_id2 = container.crawl(crawl_type=CrawlerContainer.CRAWL_TYPE_SOCIALDATA, request=request2)

        self.assertEqual(container.get_size(), 2)
        self.assertTrue(crawl_id1 is not None)
        self.assertTrue(crawl_id2 is not None)
        self.assertTrue(crawl_id1 != crawl_id2)

    def test_crawl__trim__no_data(self):
        container = CrawlerContainerAlchemy(records_size = 3, db_path=self.db_name)

        self.assertEqual(container.get_size(), 0)

        request1 = PageRequestObject("https://youtube.com/1")
        request2 = PageRequestObject("https://youtube.com/2")
        request3 = PageRequestObject("https://youtube.com/3")
        request4 = PageRequestObject("https://youtube.com/4")
        request5 = PageRequestObject("https://youtube.com/5")

        # call tested function
        crawl_id1 = container.crawl(crawl_type=CrawlerContainer.CRAWL_TYPE_GET, request=request1)
        self.assertEqual(container.get_size(), 1)
        self.assertTrue(crawl_id1)
        self.assertTrue(container.get(crawl_id=1))

        crawl_id2 = container.crawl(crawl_type=CrawlerContainer.CRAWL_TYPE_GET, request=request2)
        self.assertEqual(container.get_size(), 2)
        self.assertTrue(crawl_id2)
        self.assertTrue(container.get(crawl_id=1))
        self.assertTrue(container.get(crawl_id=2))

        crawl_id3 = container.crawl(crawl_type=CrawlerContainer.CRAWL_TYPE_GET, request=request3)
        self.assertEqual(container.get_size(), 3)
        self.assertTrue(crawl_id3)
        self.assertTrue(container.get(crawl_id=1))
        self.assertTrue(container.get(crawl_id=2))
        self.assertTrue(container.get(crawl_id=3))

        crawl_id4 = container.crawl(crawl_type=CrawlerContainer.CRAWL_TYPE_GET, request=request4)
        self.assertEqual(container.get_size(), 3)
        self.assertFalse(crawl_id4)
        self.assertTrue(container.get(crawl_id=1))
        self.assertTrue(container.get(crawl_id=2))
        self.assertTrue(container.get(crawl_id=3))
        self.assertFalse(container.get(crawl_id=4))

        crawl_id5 = container.crawl(crawl_type=CrawlerContainer.CRAWL_TYPE_GET, request=request5)
        self.assertEqual(container.get_size(), 3)
        self.assertFalse(crawl_id5)
        self.assertTrue(container.get(crawl_id=1))
        self.assertTrue(container.get(crawl_id=2))
        self.assertTrue(container.get(crawl_id=3))
        self.assertFalse(container.get(crawl_id=4))
        self.assertFalse(container.get(crawl_id=5))

    def test_crawl__trim__with_data(self):
        container = CrawlerContainerAlchemy(records_size = 3, db_path=self.db_name)

        self.assertEqual(container.get_size(), 0)

        request1 = PageRequestObject("https://youtube.com/1")
        request2 = PageRequestObject("https://youtube.com/2")
        request3 = PageRequestObject("https://youtube.com/3")
        request4 = PageRequestObject("https://youtube.com/4")
        request5 = PageRequestObject("https://youtube.com/5")

        # call tested function
        crawl_id1 = container.crawl(crawl_type=CrawlerContainer.CRAWL_TYPE_GET, request=request1)
        self.assertEqual(container.get_size(), 1)
        self.assertTrue(crawl_id1)
        self.assertTrue(container.get(crawl_id=1))
        container.update(crawl_id=crawl_id1, data=[])

        crawl_id2 = container.crawl(crawl_type=CrawlerContainer.CRAWL_TYPE_GET, request=request2)
        self.assertEqual(container.get_size(), 2)
        self.assertTrue(crawl_id2)
        self.assertTrue(container.get(crawl_id=1))
        self.assertTrue(container.get(crawl_id=2))
        container.update(crawl_id=crawl_id2, data=[])

        crawl_id3 = container.crawl(crawl_type=CrawlerContainer.CRAWL_TYPE_GET, request=request3)
        self.assertEqual(container.get_size(), 3)
        self.assertTrue(crawl_id3)
        self.assertTrue(container.get(crawl_id=1))
        self.assertTrue(container.get(crawl_id=2))
        self.assertTrue(container.get(crawl_id=3))
        container.update(crawl_id=crawl_id3, data=[])

        crawl_id4 = container.crawl(crawl_type=CrawlerContainer.CRAWL_TYPE_GET, request=request4)
        self.assertEqual(container.get_size(), 3)
        self.assertTrue(crawl_id4)
        self.assertFalse(container.get(crawl_id=1))
        self.assertTrue(container.get(crawl_id=2))
        self.assertTrue(container.get(crawl_id=3))
        self.assertTrue(container.get(crawl_id=4))
        container.update(crawl_id=crawl_id4, data=[])

        crawl_id5 = container.crawl(crawl_type=CrawlerContainer.CRAWL_TYPE_GET, request=request5)
        self.assertEqual(container.get_size(), 3)
        self.assertTrue(crawl_id5)
        self.assertFalse(container.get(crawl_id=1))
        self.assertFalse(container.get(crawl_id=2))
        self.assertTrue(container.get(crawl_id=3))
        self.assertTrue(container.get(crawl_id=4))
        self.assertTrue(container.get(crawl_id=5))
        container.update(crawl_id=crawl_id5, data=[])

    def test_crawl__removes_container_adds_to_queue(self):
        container = CrawlerContainerAlchemy(records_size = 2, db_path=self.db_name)

        self.assertEqual(container.get_size(), 0)

        request1 = PageRequestObject("https://youtube.com/1")
        request2 = PageRequestObject("https://youtube.com/2")
        request3 = PageRequestObject("https://youtube.com/3")

        # call tested function
        crawl_id1 = container.crawl(crawl_type=CrawlerContainer.CRAWL_TYPE_GET, request=request1)
        container.update(crawl_id=crawl_id1, data=[])

        # call tested function
        crawl_id2 = container.crawl(crawl_type=CrawlerContainer.CRAWL_TYPE_GET, request=request2)
        container.update(crawl_id=crawl_id2, data=[])

        # we have full container, with data

        crawl_id3 = container.crawl(crawl_type=CrawlerContainer.CRAWL_TYPE_GET, request=request3)

        self.assertEqual(container.get_size(), 2)
        self.assertTrue(crawl_id3)

    def test_update__true(self):
        container = CrawlerContainerAlchemy(db_path=self.db_name)

        self.assertEqual(container.get_size(), 0)

        request = PageRequestObject("https://youtube.com")

        crawl_id = container.crawl(crawl_type=CrawlerContainer.CRAWL_TYPE_GET, request=request)

        self.assertEqual(container.get_size(), 1)
        self.assertTrue(crawl_id is not None)

        # call tested function
        result = container.update(crawl_id=crawl_id, data=get_data)
        self.assertEqual(container.get_size(), 1)
        self.assertTrue(result)

    def test_update__false(self):
        container = CrawlerContainerAlchemy(db_path=self.db_name)

        self.assertEqual(container.get_size(), 0)

        request = PageRequestObject("https://youtube.com")

        crawl_id = container.crawl(crawl_type=CrawlerContainer.CRAWL_TYPE_GET, request=request)

        self.assertEqual(container.get_size(), 1)
        self.assertTrue(crawl_id is not None)

        # call tested function
        result = container.update(crawl_id=1000, data=get_data)
        self.assertEqual(container.get_size(), 1)
        self.assertFalse(result)

    def test_update__two(self):
        container = CrawlerContainerAlchemy(db_path=self.db_name)

        self.assertEqual(container.get_size(), 0)

        request1 = PageRequestObject("https://youtube.com")
        request2 = PageRequestObject("https://github.com")

        crawl_id_get = container.crawl(crawl_type=CrawlerContainer.CRAWL_TYPE_GET, request=request1)
        crawl_id_social = container.crawl(crawl_type=CrawlerContainer.CRAWL_TYPE_SOCIALDATA, request=request2)

        self.assertEqual(container.get_size(), 2)
        self.assertTrue(crawl_id_get is not None)
        self.assertTrue(crawl_id_social is not None)

        # call tested function
        result = container.update(crawl_id=crawl_id_get, data=get_data)
        self.assertEqual(container.get_size(), 2)
        self.assertTrue(result)

        crawl_item = container.get(crawl_id=crawl_id_get)
        self.assertTrue(crawl_item)
        self.assertTrue(crawl_item.data)

        crawl_item = container.get(crawl_id=crawl_id_social)
        self.assertTrue(crawl_item)
        self.assertFalse(crawl_item.data)

    def test_find__true(self):
        container = CrawlerContainerAlchemy(db_path=self.db_name)

        self.assertEqual(container.get_size(), 0)
        request = PageRequestObject("https://youtube.com")

        crawl_id = container.crawl(crawl_type=CrawlerContainer.CRAWL_TYPE_GET, request=request)

        self.assertEqual(container.get_size(), 1)
        self.assertTrue(crawl_id is not None)

        # call tested function
        find_crawl_id = container.find(crawl_type=CrawlerContainer.CRAWL_TYPE_GET, request=request)
        self.assertTrue(find_crawl_id is not None)

    def test_find__false__not_link(self):
        container = CrawlerContainerAlchemy(db_path=self.db_name)

        self.assertEqual(container.get_size(), 0)

        request = PageRequestObject("https://youtube.com")

        crawl_id = container.crawl(crawl_type=CrawlerContainer.CRAWL_TYPE_GET, request=request)

        self.assertEqual(container.get_size(), 1)
        self.assertTrue(crawl_id is not None)

        request = PageRequestObject("https://youtube.com/1")

        # call tested function
        find_crawl_id = container.find(crawl_type=CrawlerContainer.CRAWL_TYPE_GET, request=request)
        self.assertTrue(find_crawl_id is None)

    def test_find__false__crawler_name(self):
        container = CrawlerContainerAlchemy(db_path=self.db_name)

        self.assertEqual(container.get_size(), 0)

        request = PageRequestObject("https://youtube.com")
        request.crawler_name = "test"

        crawl_id = container.crawl(crawl_type=CrawlerContainer.CRAWL_TYPE_GET, request=request)

        self.assertEqual(container.get_size(), 1)
        self.assertTrue(crawl_id is not None)

        request = PageRequestObject("https://youtube.com")
        request.crawler_name = "not test"

        # call tested function
        find_crawl_id = container.find(crawl_type=CrawlerContainer.CRAWL_TYPE_GET, request=request)
        self.assertTrue(find_crawl_id is None)

    def test_find__false__invalid_type(self):
        container = CrawlerContainerAlchemy(db_path=self.db_name)

        self.assertEqual(container.get_size(), 0)

        request = PageRequestObject("https://youtube.com")

        crawl_id = container.crawl(crawl_type=CrawlerContainer.CRAWL_TYPE_GET, request=request)

        self.assertEqual(container.get_size(), 1)
        self.assertTrue(crawl_id is not None)

        # call tested function
        find_crawl_id = container.find(crawl_type=CrawlerContainer.CRAWL_TYPE_SOCIALDATA, request=request)
        self.assertTrue(find_crawl_id is None)

    def test_get__by_id_true(self):
        container = CrawlerContainerAlchemy(db_path=self.db_name)

        self.assertEqual(container.get_size(), 0)

        request = PageRequestObject("https://youtube.com")

        crawl_id = container.crawl(crawl_type=CrawlerContainer.CRAWL_TYPE_GET, request=request)

        self.assertEqual(container.get_size(), 1)
        self.assertTrue(crawl_id is not None)

        # call tested function
        get_crawl_data = container.get(crawl_id=crawl_id)
        self.assertTrue(get_crawl_data is not None)

    def test_get__by_id_false(self):
        container = CrawlerContainerAlchemy(db_path=self.db_name)

        self.assertEqual(container.get_size(), 0)

        request = PageRequestObject("https://youtube.com")

        crawl_id = container.crawl(crawl_type=CrawlerContainer.CRAWL_TYPE_GET, request=request)

        self.assertEqual(container.get_size(), 1)
        self.assertTrue(crawl_id is not None)

        # call tested function
        get_crawl_data = container.get(crawl_id=1000)
        self.assertTrue(get_crawl_data is None)

    def test_get__two(self):
        container = CrawlerContainerAlchemy(db_path=self.db_name)

        self.assertEqual(container.get_size(), 0)

        request1 = PageRequestObject("https://youtube.com")
        request2 = PageRequestObject("https://github.com")

        crawl_id_get = container.crawl(crawl_type=CrawlerContainer.CRAWL_TYPE_GET, request=request1)
        crawl_id_social = container.crawl(crawl_type=CrawlerContainer.CRAWL_TYPE_SOCIALDATA, request=request2)

        self.assertEqual(container.get_size(), 2)
        self.assertTrue(crawl_id_get is not None)
        self.assertTrue(crawl_id_social is not None)

        result = container.update(crawl_id=crawl_id_get, data=get_data)
        self.assertEqual(container.get_size(), 2)
        self.assertTrue(result)

        # call tested function
        crawl_item = container.get(crawl_id=crawl_id_get)
        self.assertTrue(crawl_item)
        self.assertTrue(crawl_item.data)

        # call tested function
        crawl_item = container.get(crawl_id=crawl_id_social)
        self.assertTrue(crawl_item)
        self.assertFalse(crawl_item.data)

    def test_add__crawl_id(self):
        container = CrawlerContainerAlchemy(db_path=self.db_name)

        self.assertEqual(container.get_size(), 0)

        request = PageRequestObject("https://youtube.com")

        crawl_id = container.crawl(crawl_type=CrawlerContainer.CRAWL_TYPE_GET, request=request)

        data = {"test_data" : "OK"}

        container.add(crawl_id=crawl_id, data=data)

        crawl_item = container.get(crawl_id=crawl_id)
        self.assertTrue(crawl_item.data)
        self.assertIn("test_data", crawl_item.data)

    def test_add__request(self):
        container = CrawlerContainerAlchemy(db_path=self.db_name)

        self.assertEqual(container.get_size(), 0)

        request = PageRequestObject("https://youtube.com")
        crawl_id = container.crawl(crawl_type=CrawlerContainer.CRAWL_TYPE_GET, request=request)

        data = {"test_data" : "OK"}

        container.add(request=request, data=data)

        crawl_item = container.get(crawl_id=crawl_id)
        self.assertTrue(crawl_item.data)
        self.assertIn("test_data", crawl_item.data)

    def test_expire_old__with_data__one(self):
        container = CrawlerContainerAlchemy(db_path=self.db_name)

        self.assertEqual(container.get_size(), 0)

        request = PageRequestObject("https://youtube.com")
        crawl_id = container.crawl(crawl_type=CrawlerContainer.CRAWL_TYPE_GET, request=request)

        self.assertEqual(container.get_size(), 1)

        for item in container.container:
            item.timestamp = datetime.now() - timedelta(minutes=10000)
            item.data = []  # we have the data

        # call tested function
        container.expire_old()

        self.assertEqual(container.get_size(), 0)

    def test_expire_old__with_data__many(self):
        container = CrawlerContainerAlchemy(records_size = 3, db_path=self.db_name)

        self.assertEqual(container.get_size(), 0)

        request1 = PageRequestObject("https://youtube.com/1")
        request2 = PageRequestObject("https://youtube.com/2")
        request3 = PageRequestObject("https://youtube.com/3")
        request4 = PageRequestObject("https://youtube.com/4")

        crawl_id1 = container.crawl(crawl_type=CrawlerContainer.CRAWL_TYPE_GET, request=request1)
        crawl_id2 = container.crawl(crawl_type=CrawlerContainer.CRAWL_TYPE_GET, request=request2)
        crawl_id3 = container.crawl(crawl_type=CrawlerContainer.CRAWL_TYPE_GET, request=request3)

        self.assertEqual(container.get_size(), 3)

        for item in container.container:
            item.timestamp = datetime.now() - timedelta(minutes=10000)
            item.data = []  # we have the data

        # call tested function
        container.expire_old()

        self.assertEqual(container.get_size(), 0)

    def test_expire_old__without_data(self):
        container = CrawlerContainerAlchemy(db_path=self.db_name)

        self.assertEqual(container.get_size(), 0)

        request = PageRequestObject("https://youtube.com")
        crawl_id = container.crawl(crawl_type=CrawlerContainer.CRAWL_TYPE_GET, request=request)

        self.assertEqual(container.get_size(), 1)

        for item in container.container:
            item.timestamp = datetime.now() - timedelta(minutes=10000)
            item.data = None  # we don't have the data

        # call tested function
        container.expire_old()

        self.assertEqual(container.get_size(), 1)

