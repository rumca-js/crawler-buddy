"""
There is a feedparser, but

a) feedparser does not work with asyncio properly
b) it contained error, which prevented me from reading one RSS feed (it did not read entry.link)
"""

import html
import lxml.etree as ET


__version__ = "0.0.2"


class FeedObject(object):
    def __init__(self, root, ns=None):
        self.root = root
        self.ns = ns

    def get_prop(self, aproperty):
        aproperty_value = self.root.find(aproperty, self.ns)
        if aproperty_value is not None:
            if len(aproperty_value) == 0:  # No child elements
                return aproperty_value.text.strip() if aproperty_value.text else None

            parts = []
            for child in aproperty_value:
                if child.text:
                    parts.append(child.text)
                parts.append(ET.tostring(child, encoding="unicode", method="html"))
                if child.tail:
                    parts.append(child.tail)

            inner_content = "".join(parts).strip()
            return inner_content

    def get_prop_attribute(self, aproperty, attribute):
        aproperty_value = self.root.find(aproperty, self.ns)
        if aproperty_value is not None:
            if attribute in aproperty_value.attrib:
                return aproperty_value.attrib[attribute]


class FeedReaderEntry(FeedObject):
    def __init__(self, entry_data, ns):
        super().__init__(entry_data, ns)
        self.read()

    def read(self):
        if self.root is None:
            return

        self.link = self.try_to_get_attribute("link", "href")

        self.title = self.try_to_get_field("title")
        self.subtitle = self.try_to_get_field("subtitle")
        self.description = self.try_to_get_field("description")
        if not self.description:
            if "media" in self.ns:
                self.description = self.get_prop(".//media:description")
        if not self.description:
            self.description = self.get_prop("content")
        if not self.description:
            if "atom" in self.ns:
                self.description = self.get_prop("atom:content")

        self.published = self.try_to_get_field("pubDate")
        if not self.published:
            self.published = self.try_to_get_field("published")

        self.media_thumbnail = []

        if "media" in self.ns:
            media_thumbnail = self.get_prop_attribute(".//media:thumbnail", "url")
            if media_thumbnail:
                self.media_thumbnail = [{"url": media_thumbnail}]

        self.media_content = []

        if "media" in self.ns:
            media_content = self.get_prop_attribute(".//media:content", "url")
            if media_content:
                self.media_content = [{"url": media_content}]

        self.author = self.try_to_get_fields("author", "name")

        if not self.author:
            if "itunes" in self.ns:
                self.author = self.get_prop("itunes:owner/itunes:name")

        self.tags = self.try_to_get_field("tags")

        source = {}
        source["href"] = self.try_to_get_attribute("source", "href")
        if not source["href"]:
            source["href"] = self.try_to_get_fields("source", "href")
        source["url"] = self.try_to_get_attribute("source", "url")
        if not source["url"]:
            source["url"] = self.try_to_get_fields("source", "url")
        self.source = source

    def try_to_get_field(self, field):
        value = self.get_prop("./" + field)
        if not value:
            value = self.get_prop(field)
        if not value:
            if "atom" in self.ns:
                value = self.get_prop(f"atom:{field}")

        return value

    def try_to_get_fields(self, fieldone, fieldtwo):
        value = self.get_prop(f"./{fieldone}/{fieldtwo}")
        if not value:
            value = self.get_prop(f"{fieldone}/{fieldtwo}")
        if not value:
            if "atom" in self.ns:
                value = self.get_prop(f"atom:{fieldone}/atom:{fieldtwo}")

        return value

    def try_to_get_attribute(self, field, attribute):
        value = self.get_prop(".//" + field)
        if not value:
            value = self.get_prop_attribute(field, attribute)
        if not value:
            if "atom" in self.ns:
                value = self.get_prop_attribute(f"atom:{field}", attribute)

        return value

    def __contains__(self, item):
        return True


class FeedReaderFeed(FeedObject):
    def __init__(self, root, ns=None, is_atom=False):
        super().__init__(root, ns)

        self.is_atom = is_atom

    def parse(self):
        return self.read()

    def try_to_get_field(self, field):
        value = self.get_prop("./" + field)
        if not value:
            value = self.get_prop(field)
        if not value:
            value = self.get_prop(f"channel/{field}")
        if not value:
            if "atom" in self.ns:
                value = self.get_prop(f"atom:{field}")
        if not field:
            if "atom" in self.ns:
                value = self.get_prop(f"atom:channel/atom:{field}")

        return value

    def try_to_get_fields(self, fieldone, fieldtwo):
        field = self.get_prop(f"./{fieldone}/{fieldtwo}")
        if not field:
            field = self.get_prop(f"{fieldone}/{fieldtwo}")
        if not field:
            if "atom" in self.ns:
                field = self.get_prop(f"./atom:{fieldone}/atom:{fieldtwo}")
        if not field:
            if "atom" in self.ns:
                field = self.get_prop(f"atom:{fieldone}/atom:{fieldtwo}")
        if not field:
            field = self.get_prop(f"./channel/{fieldone}/{fieldtwo}")
        if not field:
            field = self.get_prop(f"channel/{fieldone}/{fieldtwo}")
        if not field:
            if "atom" in self.ns:
                field = self.get_prop(f"./atom:channel/atom:{fieldone}/atom:{fieldtwo}")
        if not field:
            if "atom" in self.ns:
                field = self.get_prop(f"atom:channel/atom:{fieldone}/atom:{fieldtwo}")

        return field

    def try_to_get_attribute(self, field, attribute):
        value = self.get_prop_attribute(field, attribute)
        if not value:
            value = self.get_prop_attribute(f"channel/{field}", attribute)
        if not value:
            if "atom" in self.ns:
                value = self.get_prop_attribute(f"atom:{field}", attribute)
        if not field:
            if "atom" in self.ns:
                value = self.get_prop_attribute(f"atom:channel/atom:{field}", attribute)

        return value

    def read(self):
        if self.root is None:
            self.title = None
            self.subtitle = None
            self.description = None
            self.language = None
            self.published = None
            self.author = None
            self.tags = []
            self.image = {}
            return

        self.title = self.try_to_get_field("title")
        self.link = self.try_to_get_field("link")
        if not self.link:
            self.link = self.try_to_get_attribute("link", "href")
        self.subtitle = self.try_to_get_field("subtitle")
        self.description = self.try_to_get_field("description")
        self.language = self.try_to_get_field("language")

        self.published = self.try_to_get_field("published")
        if not self.published:
            self.published = self.try_to_get_field("pubDate")
        if not self.published:
            self.published = self.try_to_get_field("lastBuildDate")

        self.author = self.try_to_get_fields("author", "name")
        if not self.author:
            if "itunes" in self.ns:
                self.author = self.get_prop(".//itunes:author")
        if not self.author:
            if "itunes" in self.ns:
                self.author = self.get_prop("itunes:author")
        if not self.author:
            if "itunes" in self.ns:
                self.author = self.get_prop("./channel/itunes:author")
        if not self.author:
            if "atom" in self.ns and "itunes" in self.ns:
                self.author = self.get_prop("./atom:channel/itunes:author")

        self.tags = self.try_to_get_field("tags")

        image = {}
        image["url"] = self.try_to_get_fields("image", "url")
        if not image["url"]:
            image["url"] = self.try_to_get_attribute("image", "url")
        image["href"] = self.try_to_get_fields("image", "href")
        if not image["href"]:
            if "atom" in self.ns:
                image["href"] = self.try_to_get_attribute("image", "href")
        image["width"] = self.try_to_get_fields("image", "width")
        image["height"] = self.try_to_get_fields("image", "height")
        self.image = image

    def __contains__(self, item):
        return True


class FeedReader(object):
    def __init__(self, contents):
        self.contents = contents.strip()

        self.process_html()

        self.ns = {}
        self.root = None

    def parse(contents):
        r = FeedReader(contents)
        r.parse_implementation()
        return r

    def parse_implementation(self):
        # initial?
        self.feed = FeedReaderFeed(self.root, self.ns, is_atom=True)
        self.feed.parse()
        self.entries = []

        if not self.contents:
            return

        try:
            # recover - from errors, additional texts should not lead to processing errors
            # RSS feeds use CDATA for titles etc.
            parser = ET.XMLParser(strip_cdata=False, recover=True)
            self.root = ET.fromstring(self.contents.encode(), parser=parser)
        except Exception as E:
            print(str(E))
            self.root = None

        if self.root is not None:
            self.ns = self.root.nsmap

        is_atom = "atom" in self.ns

        self.feed = FeedReaderFeed(self.root, ns=self.ns, is_atom=is_atom)
        self.feed.parse()

        entries = self.get_entries()
        if not entries:
            entries = self.get_items()

        if entries:
            self.read_entries(entries)

    def process_html(self):
        # TODO what if we have < html?
        html_wh = self.contents.strip().find("<html")

        if html_wh != -1:
            rss_wh = self.contents.strip().find("<rss")
            if rss_wh != -1:
                if self.process_html_raw("rss"):
                    return True

            feed_wh = self.contents.strip().find("<feed")
            if feed_wh != -1:
                if self.process_html_raw("feed"):
                    return True

            rss_wh = self.contents.strip().find("&gt;rss")
            if rss_wh != -1:
                if self.process_html_encoded():
                    return True

    def process_html_raw(self, tag):
        wh = self.contents.find("<" + tag)
        if wh == -1:
            return False

        last_wh = self.contents.rfind("</{}>".format(tag))
        if last_wh == -1:
            return False

        # +4 to compensate for &gt; text
        self.contents = self.contents[wh : last_wh + 6]

        return True

    def process_html_encoded(self):
        wh = self.contents.find("&lt;")
        if wh == -1:
            return False

        last_wh = self.contents.rfind("&gt;")
        if last_wh == -1:
            return False

        # +4 to compensate for &gt; text
        self.contents = self.contents[wh : last_wh + 4]
        self.contents = html.unescape(self.contents)

        return True

    def read_entries(self, entries):
        for entry in entries:
            self.entries.append(FeedReaderEntry(entry, self.ns))

    def get_entries(self):
        if self.root is None:
            return

        entries = self.root.findall(".//entry", self.ns)
        if len(entries) > 0:
            return entries

        if "atom" in self.ns:
            entries = self.root.findall(".//atom:entry", self.ns)
            if len(entries) > 0:
                return entries

    def get_items(self):
        if self.root is None:
            return

        entries = self.root.findall(".//item", self.ns)
        if len(entries) > 0:
            return entries

        if "atom" in self.ns:
            entries = self.root.findall(".//atom:item", self.ns)
            if len(entries) > 0:
                return entries
