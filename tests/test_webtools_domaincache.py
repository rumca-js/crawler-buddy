from src.webtools import Url, DomainCache, DomainCacheInfo

from tests.fakeinternet import FakeInternetTestCase, MockRequestCounter


class PageResponseObjectTest(FakeInternetTestCase):
    def setUp(self):
        self.disable_web_pages()


class DomainCacheInfoTest(FakeInternetTestCase):
    def setUp(self):
        self.disable_web_pages()

    def test_cache_info__constructor(self):
        MockRequestCounter.mock_page_requests = 0

        # call tested function
        cache = DomainCache(cache_size=5, respect_robots_txt=True)
        cache_info = cache.get_domain_info("https://robots-txt.com/page.html")

        self.assertTrue(cache_info)

    def test_cache_info__url(self):
        MockRequestCounter.mock_page_requests = 0

        # call tested function
        cache = DomainCache(cache_size=5, respect_robots_txt=True)
        cache_info = cache.get_domain_info("https://robots-txt.com/page.html")

        self.assertEqual(cache_info.url, "https://robots-txt.com")

    def test_cache_info__robots_txt(self):
        MockRequestCounter.mock_page_requests = 0

        # call tested function
        cache = DomainCache(cache_size=5, respect_robots_txt=True)
        cache_info = cache.get_domain_info("https://robots-txt.com/page.html")

        self.assertEqual(
            cache_info.get_robots_txt_url(), "https://robots-txt.com/robots.txt"
        )

    def test_cache_info__is_allowed(self):
        MockRequestCounter.mock_page_requests = 0

        # call tested function
        cache = DomainCache(cache_size=5, respect_robots_txt=True)
        cache_info = cache.get_domain_info("https://robots-txt.com/page.html")

        self.assertTrue(cache_info.is_allowed("https://robots-txt.com"))
        self.assertTrue(cache_info.is_allowed("https://robots-txt.com/robots.txt"))
        self.assertTrue(cache_info.is_allowed("https://robots-txt.com/anything"))
        self.assertFalse(cache_info.is_allowed("https://robots-txt.com/admin/"))
        self.assertTrue(cache_info.is_allowed("https://robots-txt.com/admin"))

    def test_cache_info__limit(self):
        MockRequestCounter.mock_page_requests = 0

        # call tested function
        cache = DomainCache(cache_size=5, respect_robots_txt=True)

        for key in range(1, 10):
            cache_info = cache.get_domain_info(
                "https://robots-txt{}.com/page.html".format(key)
            )

        self.assertEqual(len(cache.cache), 5)

    def test_cache_info__invalid_page(self):
        MockRequestCounter.mock_page_requests = 0

        # call tested function
        cache = DomainCache(cache_size=5, respect_robots_txt=True)

        cache_info = cache.get_domain_info(
            "https://page-with-http-status-500.com"
        )

        # call tested function
        cache_info.is_allowed("https://page-with-http-status-500.com/test.html")

        # +1 for first browser, +1 for second browser
        self.assertEqual(MockRequestCounter.mock_page_requests, 1)

        cache_info = cache.get_domain_info(
            "https://page-with-http-status-500.com"
        )

        # call tested function
        cache_info.is_allowed("https://page-with-http-status-500.com/test.html")

        self.assertEqual(MockRequestCounter.mock_page_requests, 1)
