from webtoolkit import RemoteServer

from src.webtools import (
    Url,
)
from src.server_views import set_response_impl

from tests.unit.fakeinternet import FakeInternetTestCase, MockRequestCounter
from webtoolkit.tests.fakeresponse import FlaskRequest




class ScriptServerTest(FakeInternetTestCase):
    def setUp(self):
        self.disable_web_pages()

        self.response = {
           "url": "https://example.com",
           "status_code" : 200,
           "request" : {
              "url": "https://example.com",
              "crawler_name" : "Fake Properties Crawler2",
           }
        }

        self.all_properties = [
           {
               "data" : {
                   "title" : "Example Page Title",
                   "link": "https://example.com",
                   "feeds": "https://example.com/rss",
                   "date_published": "Sat, 07 Feb 2026 12:00:00 GMT",
               },
               "name" : "Properties",
           },
           {
               "data" : {},
               "name" : "Text",
           },
           {
               "data" : {
                   "https://example.com" : {
                       "status_code" : 200,
                       "request" : {
                           "url": "https://example.com",
                           "crawler_name" : "Fake Properties Crawler2",
                       },
                       "text" : "<html></html"
                   }
               },
               "name" : "Streams",
           },
           {
               "data" : {
                   "crawler_name" : "Fake Properties Crawler1",
               },
               "name" : "Request",
           },
           {
               "data" : {
                   "status_code" : 200,
                   "request" : {
                       "url": "https://example.com",
                       "crawler_name" : "Fake Properties Crawler2",
                   }
               },
               "name" : "Response",
           },
           {
               "data" : 
               [
                   {"title" : "0", "link" : "https://0.com", "date_published" : "Sat, 07 Feb 2026 12:00:00 GMT"},
                   {"title" : "1", "link" : "https://1.com", "date_published" : "Sat, 07 Feb 2026 12:00:00 GMT"},
                   {"title" : "2", "link" : "https://2.com", "date_published" : "Sat, 07 Feb 2026 12:00:00 GMT"},
               ],
               "name" : "Entries",
           },
        ]

    def test_set_response_impl(self):
        request = FlaskRequest("http://192.168.0.0")

        crawler_data = {
          "name" : "MockCrawler",
          "timeout_s" : 400,
          "settings" : {
              "script": "test/path",
          }
        }

        request.json = self.response

        # call tested function
        url = set_response_impl(request)

        self.assertTrue(url)

        all_properties = url.get_all_properties()

        self.assertTrue(all_properties)

        properties = RemoteServer.read_properties_section("Properties", all_properties)
        self.assertIn("link", properties)
        self.assertEqual(properties["link"], "https://example.com")
