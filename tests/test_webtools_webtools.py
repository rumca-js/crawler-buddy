import hashlib
from webtoolkit import (
   InputContent,
   PageOptions,
   calculate_hash,
   status_code_to_text,
)

from .fakeinternet import FakeInternetTestCase


webpage_no_lang = """<html>
</html>
"""

webpage_lang_not_default = """<html lang="it">
</html>
"""

webpage_no_title = """<html>
</html>
"""

webpage_title_lower = """<html>
 <title>This is a lower case title</title>
</html>
"""

webpage_title_upper = """<html>
 <TITLE>This is a upper case title</TITLE>
</html>
"""

webpage_title_meta_og = """<html>
 <TITLE>selected meta title</TITLE>
 <meta property="og:title" content="selected og:title" />
</html>
"""

webpage_description_meta_og = """<html>
 <description>selected meta description</TITLE>
 <meta property="og:description" content="selected og:description" />
</html>
"""

webpage_links = """<html>
 <TITLE>This is a upper case title</TITLE>
 <a custom-peroperty="custom-property-value" href="http://otherpage1.net" class="class">
   <picture></picture>
   </a>
 <a custom-peroperty="custom-property-value" href="https://otherpage2.net" class="class">
   <picture></picture>
   </a>
 <a custom-peroperty="custom-property-value" href="/test/test1" class="contentLink  hero--img -first">
   <picture></picture>
   </a>
 <a custom-peroperty="custom-property-value" href="/test/test2.html" class="class">
   <picture></picture>
   </a>
 <a custom-peroperty="custom-property-value" href="/test/test3.htm" class="class">
   <picture></picture>
   </a>
 <a custom-peroperty="custom-property-value" href="/test/test4.js" class="class">
   <picture></picture>
   </a>
 <a custom-peroperty="custom-property-value" href="/test/test5/" class="class">
   <picture></picture>
   </a>
 <a custom-peroperty="custom-property-value" href="//test6.domain.com/" class="class">
   <picture></picture>
   </a>
</html>
"""


class PageOptionsTest(FakeInternetTestCase):
    def setUp(self):
        self.disable_web_pages()

    def test_get_crawler(self):
        o = PageOptions()
        o.mode_mapping = [
                {
                    "name" : "test",
                    "crawler" : "test",
                    "settings" : {},
                },
                {
                    "name" : "test2",
                    "crawler" : "test2",
                    "settings" : {},
                },
        ]

        # call tested function
        self.assertTrue(o.get_crawler("test"))

        # call tested function
        self.assertFalse(o.get_crawler("notest"))

    def test_bring_to_frong(self):
        o = PageOptions()
        o.mode_mapping = [
                {
                    "name" : "test1",
                    "crawler" : "test1",
                    "settings" : {},
                },
                {
                    "name" : "test2",
                    "crawler" : "test2",
                    "settings" : {},
                },
                {
                    "name" : "test3",
                    "crawler" : "test3",
                    "settings" : {},
                },
        ]

        crawler = o.get_crawler("test2")
        self.assertTrue(crawler)

        # call tested function
        o.bring_to_front(crawler)

        self.assertEqual(o.mode_mapping[0]["crawler"], "test2")
        self.assertEqual(o.mode_mapping[1]["crawler"], "test1")


class InputContentTest(FakeInternetTestCase):
    def setUp(self):
        self.disable_web_pages()

    def test_htmlify_two_normal_links(self):
        content = """this is <a href="https://first-link.com">First Link</a>
        this is <a href="https://second-link.com">Second Link</a>"""

        c = InputContent(content)
        # call tested function
        result = c.htmlify()
        self.assertEqual(result, content)

    def test_htmlify_pure_links(self):
        content = """this is https://first-link.com
        this is https://second-link.com"""

        c = InputContent(content)
        # call tested function
        result = c.htmlify()

        expected_result = """this is <a href="https://first-link.com">https://first-link.com</a>
        this is <a href="https://second-link.com">https://second-link.com</a>"""

        self.assertEqual(result, expected_result)

    def test_htmlify_removes_attrs(self):
        content = """this is <a href="https://first-link.com" style="clear:both">First Link</a>
        this is <a href="https://second-link.com" style="display:flex">Second Link</a>"""

        c = InputContent(content)
        # call tested function
        result = c.htmlify()

        expected_result = """this is <a href="https://first-link.com">First Link</a>
        this is <a href="https://second-link.com">Second Link</a>"""

        self.assertEqual(result, expected_result)

class WebToolsTest(FakeInternetTestCase):
    def setUp(self):
        self.disable_web_pages()

    def test_status_code_to_text(self):
        text = status_code_to_text(200)
        # call tested function
        self.assertTrue(text)

    def test_status_code_to_text(self):
        text = status_code_to_text(403)
        # call tested function
        self.assertTrue(text)

    def test_status_code_to_text(self):
        text = status_code_to_text(600)
        # call tested function
        self.assertTrue(text)
