from time import strptime
from bs4 import BeautifulSoup
import re
import json
from datetime import datetime
from dateutil import parser
import html
import lxml.etree as ET

from utils.dateutils import DateUtils

from .webtools import (
    calculate_hash,
    WebLogger,
    date_str_to_date,
)
from .urllocation import UrlLocation
from .feedreader import FeedReader


class ContentInterface(object):
    def __init__(self, url, contents):
        self.url = url
        self.contents = contents

    def get_contents(self):
        return self.contents

    def get_title(self):
        raise NotImplementedError

    def get_description(self):
        raise NotImplementedError

    def get_language(self):
        raise NotImplementedError

    def get_thumbnail(self):
        raise NotImplementedError

    def get_author(self):
        raise NotImplementedError

    def get_album(self):
        raise NotImplementedError

    def get_tags(self):
        raise NotImplementedError

    def get_url(self):
        return self.url

    def get_canonical_url(self):
        return self.url

    def get_page_rating(self):
        """
        Default behavior
        """
        rating_vector = self.get_page_rating_vector()
        link_rating = self.get_link_rating()
        rating_vector.extend(link_rating)

        page_rating = 0
        max_page_rating = 0
        for rating in rating_vector:
            page_rating += rating[0]
            max_page_rating += rating[1]

        if page_rating == 0:
            return 0
        if max_page_rating == 0:
            return 0

        page_rating = (float(page_rating) * 100.0) / float(max_page_rating)

        try:
            return int(page_rating)
        except ValueError:
            return 0

    def get_page_rating_vector(self):
        """
        Returns vector of tuples.
        Each tuple contains actual rating for property, and max rating for that property
        """
        result = []

        if self.get_title() is not None and str(self.get_title()) != "":
            result.append([10, 10])

        if self.get_description() is not None and str(self.get_description()) != "":
            result.append([5, 5])

        if self.get_language() is not None and str(self.get_language()) != "":
            result.append([1, 1])

        if self.get_thumbnail() is not None and str(self.get_thumbnail()) != "":
            result.append([1, 1])

        if (
            self.get_date_published() is not None
            and str(self.get_date_published()) != ""
        ):
            result.append([1, 1])

        return result

    def get_date_published(self):
        """
        This should be date. Not string
        """
        raise NotImplementedError

    def get_contents_hash(self):
        contents = self.get_contents()
        if contents:
            return calculate_hash(contents)

    def get_contents_body_hash(self):
        return self.get_contents_hash()

    def get_properties(self):
        props = {}

        props["link"] = self.url
        props["title"] = self.get_title()
        props["description"] = self.get_description()
        props["author"] = self.get_author()
        props["album"] = self.get_album()
        props["thumbnail"] = self.get_thumbnail()
        props["language"] = self.get_language()
        props["page_rating"] = self.get_page_rating()
        props["date_published"] = self.get_date_published()
        props["tags"] = self.get_tags()
        props["link_canonical"] = self.get_canonical_url()

        return props

    def is_cloudflare_protected(self):
        """
        Should not obtain contents by itself

        You'd probably be more successful trying to not trigger
        the bot detection in the first place rather than trying to bypass it after the fact.
        """
        contents = self.contents

        if contents:
            if contents.find("https://challenges.cloudflare.com") >= 0:
                return True

        return False

    def guess_date(self):
        """
        This is ugly, but dateutil.parser does not work. May generate exceptions.
        Ugly is better than not working.

        Supported formats:
         - Jan. 15, 2024
         - Jan 15, 2024
         - January 15, 2024
         - 15 January 2024 14:48 UTC
        """

        content = self.get_contents()
        if not content:
            return

        # searching will be case insensitive
        content = content.lower()

        # Get the current year
        try:
            current_year = int(datetime.now().year)
        except ValueError:
            # TODO fix this
            current_year = 2024

        # Define regular expressions
        current_year_pattern = re.compile(rf"\b{current_year}\b")
        four_digit_number_pattern = re.compile(r"\b\d{4}\b")

        # Attempt to find the current year in the string
        match_current_year = current_year_pattern.search(content)

        year = None
        scope = None

        if match_current_year:
            try:
                year = int(current_year)
            except ValueError:
                # TODO fix this
                year = 2024

            # Limit the scope to a specific portion before and after year
            scope = content[
                max(0, match_current_year.start() - 15) : match_current_year.start()
                + 20
            ]
        else:
            match_four_digit_number = four_digit_number_pattern.search(content)
            if match_four_digit_number:

                try:
                    year = int(match_four_digit_number.group(0))

                    # Limit the scope to a specific portion before and after year
                    scope = content[
                        max(
                            0, match_four_digit_number.start() - 15
                        ) : match_four_digit_number.start()
                        + 20
                    ]
                except ValueError:
                    return

        if scope:
            return self.guess_by_scope(scope, year)

    def guess_by_scope(self, scope, year):
        date_pattern_iso = re.compile(r"(\d{4})-(\d{1,2})-(\d{1,2})")

        month_re = "(jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)\.?"

        # 2024 jan 23
        date_pattern_us = re.compile(
            r"(\d{4})\s*{}\s*(\d{1,2})".replace("{}", month_re)
        )
        # jan 23 2024
        date_pattern_us2 = re.compile(
            r"{}\s*(\d{1,2})\s*(\d{4})".replace("{}", month_re)
        )
        # 23 jan 2024
        date_pattern_ue = re.compile(
            r"(\d{1,2})\s*{}\s*(\d{4})".replace("{}", month_re)
        )

        # only Jan 23, without year next by
        month_date_pattern = re.compile(r"\b{}\s*(\d+)\b".replace("{}", month_re))

        date_pattern_iso_match = date_pattern_iso.search(scope)
        date_pattern_us_match = date_pattern_us.search(scope)
        date_pattern_us2_match = date_pattern_us2.search(scope)
        date_pattern_ue_match = date_pattern_ue.search(scope)

        month_date_pattern_match = month_date_pattern.search(scope)

        date_object = None

        if date_pattern_iso_match:
            year, month, day = date_pattern_iso_match.groups()
            date_object = self.format_date(year, month, day)

        elif date_pattern_us_match:
            year, month, day = date_pattern_us_match.groups()
            date_object = self.format_date(year, month, day)

        elif date_pattern_us2_match:
            month, day, year = date_pattern_us2_match.groups()
            date_object = self.format_date(year, month, day)

        elif date_pattern_ue_match:
            day, month, year = date_pattern_ue_match.groups()
            date_object = self.format_date(year, month, day)

        # If a month and day are found, construct a datetime object with year, month, and day
        elif month_date_pattern_match:
            month, day = month_date_pattern_match.groups()
            date_object = self.format_date(year, month, day)

        # elif year:
        #    current_year = int(datetime.now().year)

        #    if year >= current_year or year < 1900:
        #        date_object = datetime.now()
        #    else:
        #        # If only the year is found, construct a datetime object with year
        #        date_object = datetime(year, 1, 1)

        # For other scenario to not provide any value

        if date_object:
            date_object = DateUtils.to_utc_date(date_object)

        return date_object

    def format_date(self, year, month, day):
        month_number = None

        try:
            month_number = int(month)
            month_number = month
        except ValueError as E:
            WebLogger.debug("Error:{}".format(str(E)))

        if not month_number:
            try:
                month_number = strptime(month, "%b").tm_mon
                month_number = str(month_number)
            except Exception as E:
                WebLogger.debug("Error:{}".format(str(E)))

        if not month_number:
            try:
                month_number = strptime(month, "%B").tm_mon
                month_number = str(month_number)
            except Exception as E:
                WebLogger.debug("Error:{}".format(str(E)))

        if month_number is None:
            WebLogger.debug(
                "Guessing date error: URL:{};\nYear:{};\nMonth:{}\nDay:{}".format(
                    self.url, year, month, day
                )
            )
            return

        try:
            date_object = datetime.strptime(
                f"{year}-{month_number.zfill(2)}-{day.zfill(2)}", "%Y-%m-%d"
            )

            return date_object
        except Exception as E:
            WebLogger.debug(
                "Guessing date error: URL:{};\nYear:{};\nMonth:{}\nDay:{}".format(
                    self.url, year, month, day
                )
            )

    def get_position_of_html_tags(self):
        if not self.contents:
            return -1

        lower = self.contents.lower()
        if lower.find("<html") >= 0 and lower.find("<body") >= 0:
            return lower.find("<html")

        lower = self.contents.lower()
        if lower.find("<html") >= 0 and lower.find("<meta") >= 0:
            return lower.find("<html")

        return -1

    def get_position_of_rss_tags(self):
        if not self.contents:
            return -1

        lower = self.contents.lower()
        if lower.find("<rss") >= 0 and lower.find("<channel") >= 0:
            return lower.find("<rss")
        if lower.find("<feed") >= 0 and lower.find("<entry") >= 0:
            return lower.find("<feed")
        if lower.find("<rdf") >= 0 and lower.find("<channel") >= 0:
            return lower.find("<rdf")

        return -1

    def get_link_rating(self):
        rating = []

        if self.url.startswith("https://"):
            rating.append([1, 1])
        elif self.url.startswith("ftp://"):
            rating.append([1, 1])
        elif self.url.startswith("smb://"):
            rating.append([1, 1])
        elif self.url.startswith("http://"):
            rating.append([0, 1])
        else:
            rating.append([0, 1])

        p = UrlLocation(self.url)
        if p.is_domain():
            rating.append([1, 1])

        domain_only = p.get_domain_only()
        if domain_only.count(".") == 1:
            rating.append([2, 2])
        elif domain_only.count(".") == 2:
            rating.append([1, 2])
        else:
            rating.append([0, 2])

        # as example https://www.youtube.com has 23 chars

        if len(self.url) < 25:
            rating.append([2, 2])
        elif len(self.url) < 30:
            rating.append([1, 2])
        else:
            rating.append([0, 2])

        return rating


class DefaultContentPage(ContentInterface):
    def __init__(self, url, contents=""):
        super().__init__(url=url, contents=contents)

    def get_title(self):
        return None

    def get_description(self):
        return None

    def get_language(self):
        return None

    def get_thumbnail(self):
        return None

    def get_author(self):
        return None

    def get_album(self):
        return None

    def get_tags(self):
        return None

    def get_date_published(self):
        """
        This should be date. Not string
        """
        return None

    def is_valid(self):
        return True

    def get_response(self):
        return ""


class JsonPage(ContentInterface):
    def __init__(self, url, contents):
        super().__init__(url=url, contents=contents)

        self.json_obj = None
        try:
            contents = self.get_contents()
            self.json_obj = json.loads(contents)
            if self.json_obj != {}:
                self.json_obj = None
        except ValueError:
            # to be expected
            WebLogger.debug("Invalid json:{}".format(contents))

    def is_valid(self):
        if self.json_obj:
            return True

    def get_title(self):
        if self.json_obj and "title" in self.json_obj:
            return str(self.json_obj["title"])

    def get_description(self):
        if self.json_obj and "description" in self.json_obj:
            return str(self.json_obj["description"])

    def get_language(self):
        if self.json_obj and "language" in self.json_obj:
            return str(self.json_obj["language"])

    def get_thumbnail(self):
        if self.json_obj and "thumbnail" in self.json_obj:
            return str(self.json_obj["thumbnail"])

    def get_author(self):
        if self.json_obj and "author" in self.json_obj:
            return str(self.json_obj["author"])

    def get_album(self):
        if self.json_obj and "album" in self.json_obj:
            return str(self.json_obj["album"])

    def get_tags(self):
        if self.json_obj and "tags" in self.json_obj:
            return str(self.json_obj["tags"])

    def get_date_published(self):
        if self.json_obj and "date_published" in self.json_obj:
            return date_str_to_date(self.json_obj["date_published"])

    def get_page_rating(self):
        return 0


class RssPageEntry(ContentInterface):
    def __init__(self, feed_index, feed_entry, url, contents, page_object_properties):
        self.feed_index = feed_index
        self.feed_entry = feed_entry
        self.url = url
        self.contents = contents
        self.page_object_properties = page_object_properties

        super().__init__(url=self.url, contents=contents)

    def get_properties(self):
        """ """
        output_map = {}

        link = None

        if "link" in self.feed_entry:
            if self.feed_entry.link != "":
                link = self.feed_entry.link
            else:
                link = self.try_to_extract_link()

        if not link:
            return output_map

        link = link.strip()

        output_map = super().get_properties()

        output_map["link"] = link
        output_map["source"] = self.url
        output_map["bookmarked"] = False
        output_map["feed_entry"] = self.feed_entry

        return output_map

    def try_to_extract_link(self):
        """
        For:
         - https://thehill.com/feed
         - https://warhammer-community.com/feed

        feedparser provide empty links
        Trying to work around that issue.

        RSS can have <entry, or <item things inside

        TODO this should be parsed using beautiful soup
        """
        contents = self.contents

        item_search_wh = contents.find("<item", 0)
        entry_search_wh = contents.find("<entry", 0)

        index = 0
        wh = 0
        while index <= self.feed_index:
            if item_search_wh >= 0:
                wh = contents.find("<item", wh + 1)
                if wh == -1:
                    return
            if entry_search_wh >= 0:
                wh = contents.find("<entry", wh + 1)
                if wh == -1:
                    return

            index += 1

        wh = contents.find("<link", wh + 1)
        if wh == -1:
            return

        wh = contents.find(">", wh + 1)
        if wh == -1:
            return

        wh2 = contents.find("<", wh + 1)
        if wh2 == -1:
            return

        text = contents[wh + 1 : wh2]

        return text

    def get_title(self):
        return self.feed_entry.title

    def get_description(self):
        if hasattr(self.feed_entry, "description"):
            return self.feed_entry.description
        else:
            return ""

    def get_thumbnail(self):
        if hasattr(self.feed_entry, "media_thumbnail"):
            if len(self.feed_entry.media_thumbnail) > 0:
                thumb = self.feed_entry.media_thumbnail[0]
                if "url" in thumb:
                    return thumb["url"]
                else:
                    return str(thumb)
        if hasattr(self.feed_entry, "media_content"):
            if len(self.feed_entry.media_content) > 0:
                thumb = self.feed_entry.media_content[0]
                if "url" in thumb:
                    return thumb["url"]
                else:
                    return str(thumb)

        return None

    def get_language(self):
        if "language" in self.page_object_properties:
            return self.page_object_properties["language"]

    def get_date_published(self):
        date = self.get_date_published_implementation()

        now = DateUtils.get_datetime_now_utc()

        if not date:
            date = now
        if date > now:
            date = now

        return date

    def get_date_published_implementation(self):
        if hasattr(self.feed_entry, "published"):
            if not self.feed_entry.published or str(self.feed_entry.published) == "":
                return DateUtils.get_datetime_now_utc()
            else:
                try:
                    dt = parser.parse(self.feed_entry.published)
                    # TODO this might not be precise, but we do not have to be precise?

                    utc = DateUtils.to_utc_date(dt)
                    return utc

                except Exception as E:
                    WebLogger.error(
                        "RSS parser {} datetime invalid feed datetime:{};\nFeed DateTime:{};\nExc:{}\n".format(
                            self.url,
                            self.feed_entry.published,
                            self.feed_entry.published,
                            str(E),
                        )
                    )
                return DateUtils.get_datetime_now_utc()

    def get_author(self):
        if "author" in self.page_object_properties:
            return self.page_object_properties["author"]

    def get_album(self):
        return ""

    def get_tags(self):
        if "tags" in self.feed_entry:
            return self.feed_entry.tags

        return None


class RssPage(ContentInterface):
    """
    Handles RSS parsing.
    Do not use feedparser directly enywhere. We use BasicPage
    which allows to define timeouts.
    """

    def __init__(self, url, contents):
        self.feed = None

        """
        Workaround for https://warhammer-community.com/feed
        """
        # TODO apply that woraround differently
        # if contents:
        #    wh = contents.find("<rss version")
        #    if wh > 0:
        #        contents = contents[wh:]

        super().__init__(url=url, contents=contents)

        if self.contents and not self.feed:
            self.process_contents()

    def process_contents(self):
        contents = self.contents
        if contents is None:
            return None

        try:
            self.feed = FeedReader.parse(contents)
            # if not self.feed.entries or len(self.feed.entries) == 0:
            #    WebLogger.error("Feed does not have any entries {}".format(self.url))

            return self.feed

        except Exception as E:
            WebLogger.exc(E, "Url:{}. RssPage, when parsing.".format(self.url))

    def get_entries(self):
        if self.feed is None:
            return

        try:
            for item in self.get_container_elements_maps():
                yield item

        except Exception as E:
            WebLogger.exc(E, "Url:{}. RSS parsing error".format(self.url))

    def get_container_elements_maps(self):
        parent_properties = {}
        parent_properties["language"] = self.get_language()
        parent_properties["author"] = self.get_author()

        contents = self.get_contents()

        for feed_index, feed_entry in enumerate(self.feed.entries):
            rss_entry = RssPageEntry(
                feed_index,
                feed_entry,
                self.url,
                contents,
                parent_properties,
            )
            entry_props = rss_entry.get_properties()

            if not entry_props:
                WebLogger.debug(
                    "No properties for feed entry:{}".format(str(feed_entry))
                )
                continue

            if "link" not in entry_props or entry_props["link"] is None:
                WebLogger.error(
                    "Url:{}. Missing link in RSS".format(self.url),
                    detail_text=str(feed_entry),
                )
                continue

            yield entry_props

    def get_contents_body_hash(self):
        if not self.contents:
            return

        #    WebLogger.error("No rss hash contents")
        #    return calculate_hash("no body hash")
        if not self.feed:
            WebLogger.error(
                "Url:{}. RssPage has contents, but feed could not been analyzed".format(
                    self.url
                )
            )
            return

        entries = str(self.feed.entries)
        if entries == "":
            if self.contents:
                return calculate_hash(self.contents)
        if entries:
            return calculate_hash(entries)

    def get_title(self):
        if self.feed is None:
            return

        if "title" in self.feed.feed:
            return self.feed.feed.title

    def get_description(self):
        if self.feed is None:
            return

        if "description" in self.feed.feed:
            return self.feed.feed.description

        if "subtitle" in self.feed.feed:
            return self.feed.feed.subtitle

    def get_link(self):
        if "link" in self.feed.feed:
            return self.feed.feed.link

    def get_language(self):
        if self.feed is None:
            return

        if "language" in self.feed.feed:
            return self.feed.feed.language

    def get_thumbnail(self):
        if self.feed is None:
            return

        image = None
        if "image" in self.feed.feed:
            if self.feed.feed.image == {}:
                return

            if "href" in self.feed.feed.image:
                try:
                    image = self.feed.feed.image["href"]
                    if image:
                        return str(image)
                except Exception as E:
                    WebLogger.debug(str(E))

            if "url" in self.feed.feed.image:
                try:
                    image = self.feed.feed.image["url"]
                    if image:
                        return str(image)
                except Exception as E:
                    WebLogger.debug(str(E))

            elif "links" in self.feed.feed.image:
                links = self.feed.feed.image["links"]
                if len(links) > 0:
                    WebLogger.error(
                        "I do not know how to process links {}".format(str(links))
                    )
            else:
                WebLogger.error(
                    '<a href="{}">{}</a> Unsupported image type for feed. Image:{}'.format(
                        self.url, self.url, str(self.feed.feed.image)
                    )
                )

        # TODO that does not work
        # if not image:
        #    if self.url.find("https://www.youtube.com/feeds/videos.xml") >= 0:
        #        image = self.get_thumbnail_manual_from_youtube()

        if image and image.lower().find("https://") == -1:
            image = UrlLocation.get_url_full(self.url, image)

        return image

    def get_author(self):
        if self.feed is None:
            return

        if "author" in self.feed.feed:
            return self.feed.feed.author

    def get_album(self):
        if self.feed is None:
            return

        return None

    def get_date_published(self):
        if self.feed is None:
            return

        if "published" in self.feed.feed:
            return date_str_to_date(self.feed.feed.published)

    def get_tags(self):
        if self.feed is None:
            return

        if "tags" in self.feed.feed:
            return self.feed.feed.tags

        return None

    def get_properties(self):
        props = super().get_properties()
        props["contents"] = self.get_contents()
        return props

    def is_valid(self):
        if self.feed and len(self.feed.entries) > 0:
            return True

        if self.get_contents().find("<feed") >= 0:
            return True
        if self.get_contents().find("<rss") >= 0:
            return True

        # if not self.is_contents_rss():
        #     return False

        return False

    def is_contents_rss(self):
        """
        We want the checks to be simple yet effective. Check some tokens.

        There can be RSS sources in HTML, HTML inside RSS. Beware
        """
        if not self.contents:
            return

        # html_tags = self.get_position_of_html_tags()
        rss_tags = self.get_position_of_rss_tags()

        # if html_tags >= 0 and rss_tags >= 0:
        #    return rss_tags < html_tags
        if rss_tags >= 0:
            return True

    def get_charset(self):
        """
        TODO read from encoding property of xml
        """
        if not self.contents:
            return None

        if self.contents.find("encoding") >= 0:
            return "utf-8"

    def get_feeds(self):
        return [self.url]


class RssContentReader(object):
    def __init__(self, url, contents):
        self.contents = contents
        self.process()

    def process(self):
        wh_html = self.contents.find("html")
        wh_lt = self.contents.find("&lt;")

        if wh_html == -1:
            return
        if wh_lt == -1:
            return

        if wh_html > wh_lt:
            return

        wh_gt = self.contents.rfind("&gt;")
        if wh_gt == -1:
            return

        self.contents = self.contents[wh_lt : wh_gt + len("&gt;")]
        self.contents = html.unescape(self.contents)


class ContentLinkParser(ContentInterface):
    """
    TODO filter also html from non html
    """

    def __init__(self, url, contents):
        super().__init__(url=url, contents=contents)
        self.url = UrlLocation(url).get_clean_url()

    def get_links(self):
        links = set()

        links.update(self.get_links_https("https"))
        links.update(self.get_links_https_encoded("https"))
        links.update(self.get_links_https("http"))
        links.update(self.get_links_https_encoded("http"))
        links.update(self.get_links_href())

        # TODO - maybe this thing below could be made more clean, or refactored
        result = set()
        for item in links:
            wh = item.find('"')
            if wh != -1:
                item = item[:wh]
            wh = item.find("<")
            if wh != -1:
                item = item[:wh]
            wh = item.find(">")
            if wh != -1:
                item = item[:wh]
            wh = item.find("&quot;")
            if wh != -1:
                item = item[:wh]
            wh = item.find("&gt;")
            if wh != -1:
                item = item[:wh]
            wh = item.find("&lt;")
            if wh != -1:
                item = item[:wh]

            result.add(item.strip())

        links = result

        # This is most probably redundant
        if None in links:
            links.remove(None)
        if "" in links:
            links.remove("")
        if "http" in links:
            links.remove("http")
        if "https" in links:
            links.remove("https")
        if "http://" in links:
            links.remove("http://")
        if "https://" in links:
            links.remove("https://")

        result = set()
        for link in links:
            if UrlLocation(link).is_web_link():
                result.add(link)

        return links

    def get_links_https(self, protocol="https"):
        cont = str(self.get_contents())

        pattern = "(" + protocol + "?://[a-zA-Z0-9./\-_?&=#;:]+)"

        all_matches = re.findall(pattern, cont)
        # links cannot end with "."
        all_matches = [link.rstrip(".") for link in all_matches]
        return set(all_matches)

    def get_links_https_encoded(self, protocol="https"):
        cont = str(self.get_contents())

        pattern = "(" + protocol + "?:&#x2F;&#x2F;[a-zA-Z0-9./\-_?&=#;:]+)"

        all_matches = re.findall(pattern, cont)
        # links cannot end with "."
        all_matches = [link.rstrip(".") for link in all_matches]
        all_matches = [ContentLinkParser.decode_url(link) for link in all_matches]

        return all_matches

    def join_url_parts(self, partone, parttwo):
        if not partone.endswith("/"):
            partone = partone + "/"
        if parttwo.startswith("/"):
            parttwo = parttwo[1:]

        return partone + parttwo

    def decode_url(url):
        return html.unescape(url)

    def get_links_href(self):
        links = set()

        url = self.url
        domain = UrlLocation(self.url).get_domain()

        cont = str(self.get_contents())

        all_matches = re.findall('href="([a-zA-Z0-9./\-_?&=@#;:]+)', cont)

        for item in all_matches:
            ready_url = None

            item = item.strip()

            # exclude mailto: tel: sms:
            pattern = "^[a-zA-Z0-9]+:"
            if re.match(pattern, item):
                if (
                    not item.startswith("http")
                    and not item.startswith("ftp")
                    and not item.startswith("smb")
                ):
                    wh = item.find(":")
                    item = item[wh + 1 :]

            if item.startswith("//"):
                if not item.startswith("http"):
                    item = "https:" + item

            if item.startswith("/"):
                item = self.join_url_parts(domain, item)

            # for urls like user@domain.com/location
            pattern = "^[a-zA-Z0-9]+@"
            if re.match(pattern, item):
                wh = item.find("@")
                item = item[wh + 1 :]

            # not absolute path
            if not (item.startswith("http") and not item.startswith("ftp")):
                if item.count(".") <= 0:
                    item = self.join_url_parts(url, item)
                else:
                    if not item.startswith("http"):
                        item = "https://" + item

            if item.startswith("https:&#x2F;&#x2F") or item.startswith(
                "http:&#x2F;&#x2F"
            ):
                item = ContentLinkParser.decode_url(item)

            if item:
                links.add(item)

        return links

    def filter_link_html(links):
        result = set()
        for link in links:
            p = UrlLocation(link)
            if p.is_link():
                result.add(link)

        return result

    def filter_link_in_domain(links, domain):
        result = set()

        for link in links:
            if link.find(domain) >= 0:
                result.add(link)

        return result

    def filter_link_in_url(links, url):
        result = set()

        for link in links:
            if link.find(url) >= 0:
                result.add(link)

        return result

    def filter_link_out_domain(links, domain):
        result = set()

        for link in links:
            if link.find(domain) < 0:
                result.add(link)

        return result

    def filter_link_out_url(links, url):
        result = set()

        for link in links:
            if link.find(url) < 0:
                result.add(link)

        return result

    def filter_domains(links):
        result = set()
        for link in links:
            p = UrlLocation(link)
            new_link = p.get_domain()
            if new_link == "https://" or new_link == "http://":
                WebLogger.debug(
                    "Incorrect link to add: {}".format(new_link), stack=True
                )
                continue

            if not p.is_web_link():
                continue

            if new_link:
                result.add(new_link)

        return result

    def get_domains(self):
        links = self.get_links()
        links = ContentLinkParser.filter_domains(links)

        # TODO This is most probably redundant
        if None in links:
            links.remove(None)
        if "" in links:
            links.remove("")
        if "http" in links:
            links.remove("http")
        if "https" in links:
            links.remove("https")
        if "http://" in links:
            links.remove("http://")
        if "https://" in links:
            links.remove("https://")

        return links

    def get_links_inner(self):
        links = self.get_links()
        links = ContentLinkParser.filter_link_html(links)
        return ContentLinkParser.filter_link_in_domain(
            links, UrlLocation(self.url).get_domain()
        )

    def get_links_outer(self):
        links = self.get_links()
        links = ContentLinkParser.filter_link_html(links)

        in_domain = ContentLinkParser.filter_link_in_domain(
            links, UrlLocation(self.url).get_domain()
        )
        return links - in_domain


class OpmlPageEntry(ContentInterface):
    def __init__(self, url, contents, opml_entry):
        super().__init__(url=url, contents=contents)
        self.opml_entry = opml_entry
        self.title = None
        self.link = None

        self.parse()

    def parse(self):
        if "xmlUrl" in self.opml_entry.attrib:
            self.url = self.opml_entry.attrib["xmlUrl"]
        else:
            self.url = None
        if "title" in self.opml_entry.attrib:
            self.title = self.opml_entry.attrib["title"]

    def get_title(self):
        return self.title

    def get_description(self):
        pass

    def get_language(self):
        pass

    def get_thumbnail(self):
        pass

    def get_author(self):
        pass

    def get_album(self):
        pass

    def get_tags(self):
        pass


class OpmlPage(ContentInterface):
    def __init__(self, url, contents):
        """
        We could provide support for more items
        https://github.com/microsoft/rss-reader-wp/blob/master/RSSReader_WP7/sample-opml.xml
        """
        super().__init__(url=url, contents=contents)
        self.entries = []
        self.parse()

    def parse(self):
        return self.parse_implementation()

    def parse_implementation(self):
        if not self.contents:
            return

        try:
            parser = ET.XMLParser(strip_cdata=False, recover=True)
            self.root = ET.fromstring(self.contents.encode(), parser=parser)
        except Exception as E:
            print(str(E))
            self.root = None

        if self.root is None:
            return

        entries = self.root.findall(".//outline")
        if len(entries) > 0:
            for entry in entries:
                opml_entry = OpmlPageEntry(self.url, self.contents, entry)
                if opml_entry.get_url():
                    self.entries.append(opml_entry)
            return entries

    def get_entries(self):
        return self.entries

    def get_feeds(self):
        result = []
        for entry in self.entries:
            result.append(entry.get_url())

        return result

    def is_valid(self):
        if self.get_contents().find("<opml") >= 0:
            return True


class HtmlPage(ContentInterface):
    """
    Since links can be passed in various ways and formats, all links need to be "normalized" before
    returning.

    formats:
    href="images/facebook.png"
    href="/images/facebook.png"
    href="//images/facebook.png"
    href="https://images/facebook.png"
    """

    def __init__(self, url, contents):
        super().__init__(url=url, contents=contents)

        if self.contents:
            try:
                self.soup = BeautifulSoup(self.contents, "html.parser")
            except Exception as E:
                WebLogger.exc(E, "Contents type:{}".format(type(self.contents)))
                self.contents = None
                self.soup = None
        else:
            self.soup = None

    def get_head_field(self, field):
        if not self.contents:
            return None

        found_element = self.soup.find(field)
        if found_element:
            value = found_element.string
            if value != "":
                return value

    def get_meta_custom_field(self, field_type, field):
        if not self.contents:
            return None

        find_element = self.soup.find("meta", attrs={field_type: field})
        if find_element and find_element.has_attr("content"):
            return find_element["content"]

    def get_schema_field(self, itemprop):
        elements_with_itemprop = self.soup.find_all(attrs={"itemprop": True})
        for element in elements_with_itemprop:
            itemprop_v = element.get("itemprop")
            if itemprop_v != itemprop:
                continue

            if element.name == "link":
                value = element.get("href")
            elif element.name == "meta":
                value = element.get("content")
            else:
                value = element.text.strip() if element.text else None

            return value

    def get_schema_field_ex(self, itemtype, itemprop):
        """
        itemtype can be "http://schema.org/VideoObject"
        """
        # Find elements with itemtype="http://schema.org/VideoObject"
        video_objects = self.soup.find_all(attrs={"itemtype": itemtype})
        for video_object in video_objects:
            # Extract itemprop from elements inside video_object
            elements_with_itemprop = video_object.find_all(attrs={"itemprop": True})
            for element in elements_with_itemprop:
                itemprop_v = element.get("itemprop")

                if itemprop_v != itemprop:
                    continue

                if element.name == "link":
                    value = element.get("href")
                elif element.name == "meta":
                    value = element.get("content")
                else:
                    value = element.text.strip() if element.text else None

                return value

    def get_meta_field(self, field):
        if not self.contents:
            return None

        return self.get_meta_custom_field("name", field)

    def get_property_field(self, name):
        if not self.contents:
            return None

        field_find = self.soup.find("meta", property="{}".format(name))
        if field_find and field_find.has_attr("content"):
            return field_find["content"]

    def get_og_field(self, name):
        """
        Open Graph protocol: https://ogp.me/
        """
        if not self.contents:
            return None

        return self.get_property_field("og:{}".format(name))

    def get_title(self):
        if not self.contents:
            return None

        title = self.get_og_field("title")

        if not title:
            self.get_schema_field("name")

        if not title:
            title = self.get_title_meta()

        if not title:
            title = self.get_title_head()

        if not title:
            title = self.get_og_site_name()

        if title:
            title = title.strip()

            # TODO hardcoded. Some pages provide such a dumb title with redirect
            if title.find("Just a moment") >= 0:
                title = ""

        return title
        # title = html.unescape(title)

    def get_date_published(self):
        """
        There could be multiple places to read published time.
        We try every possible thing.
        """

        # used by mainstream media. Examples?
        date_str = self.get_property_field("article:published_time")
        if date_str:
            return date_str_to_date(date_str)

        # used by spotify
        date_str = self.get_meta_field("music:release_date")
        if date_str:
            return date_str_to_date(date_str)

        # used by youtube
        date_str = self.get_schema_field("datePublished")
        if date_str:
            return date_str_to_date(date_str)

    def get_title_head(self):
        if not self.contents:
            return None

        return self.get_head_field("title")

    def get_title_meta(self):
        if not self.contents:
            return None

        return self.get_meta_field("title")

    def get_description(self):
        if not self.contents:
            return None

        description = self.get_og_field("description")

        if not description:
            description = self.get_schema_field("description")

        if not description:
            description = self.get_description_meta()

        if not description:
            description = self.get_description_head()

        if description:
            description = description.strip()

        return description

    def get_description_safe(self):
        desc = self.get_description()
        if not desc:
            return ""
        return desc

    def get_description_head(self):
        if not self.contents:
            return None

        return self.get_head_field("description")

    def get_description_meta(self):
        if not self.contents:
            return None

        return self.get_meta_field("description")

    def get_thumbnail(self):
        if not self.contents:
            return None

        image = self.get_og_field("image")

        if not image:
            image = self.get_schema_field("thumbnailUrl")

        if not image:
            image = self.get_schema_field("image")

        # do not return favicon here.
        # we use thumbnails in <img, but icons do not work correctly there

        if image and image.lower().find("https://") == -1:
            image = UrlLocation.get_url_full(self.url, image)

        return image

    def get_language(self):
        if not self.contents:
            return ""

        html = self.soup.find("html")
        if html and html.has_attr("lang"):
            return html["lang"]

        locale = self.get_og_locale()
        if locale:
            return locale

        return ""

    def get_charset(self):
        if not self.contents:
            return None

        charset = None

        allmeta = self.soup.findAll("meta")
        for meta in allmeta:
            for attr in meta.attrs:
                if attr.lower() == "charset":
                    return meta.attrs[attr]
                if attr.lower() == "http-equiv":
                    if "content" in meta.attrs:
                        text = meta.attrs["content"].lower()
                        wh = text.find("charset")
                        if wh >= 0:
                            wh2 = text.find("=", wh)
                            if wh2 >= 0:
                                charset = text[wh2 + 1 :].strip()
                                return charset

    def get_author(self):
        """
        <head><author>Something</author></head>
        """
        if not self.contents:
            return None

        author = self.get_meta_field("author")
        if not author:
            author = self.get_og_field("author")

        return author

    def get_album(self):
        return None

    def get_favicons(self, recursive=False):
        if not self.contents:
            return {}

        favicons = {}

        link_finds = self.soup.find_all("link", attrs={"rel": "icon"})

        for link_find in link_finds:
            if link_find and link_find.has_attr("href"):
                full_favicon = link_find["href"]
                if full_favicon.strip() == "":
                    continue
                full_favicon = UrlLocation.get_url_full(self.url, full_favicon)
                if "sizes" in link_find:
                    favicons[full_favicon] = link_find["sizes"]
                else:
                    favicons[full_favicon] = ""

        link_finds = self.soup.find_all("link", attrs={"rel": "shortcut icon"})

        for link_find in link_finds:
            if link_find and link_find.has_attr("href"):
                full_favicon = link_find["href"]
                if full_favicon.strip() == "":
                    continue
                full_favicon = UrlLocation.get_url_full(self.url, full_favicon)
                if "sizes" in link_find:
                    favicons[full_favicon] = link_find["sizes"]
                else:
                    favicons[full_favicon] = ""

        return favicons

    def get_favicon(self):
        favicons = self.get_favicons()
        for favicon in favicons:
            return favicon

    def get_tags(self):
        if not self.contents:
            return None

        return self.get_meta_field("keywords")

    def get_canonical_url(self):
        canonical_tag = self.soup.find("link", rel="canonical")
        if canonical_tag:
            canonical_link = canonical_tag.get("href")
            if canonical_link.endswith("/"):
                return canonical_link[:-1]
            return canonical_link

        return self.url

    def get_og_title(self):
        return self.get_og_field("title")

    def get_og_description(self):
        return self.get_og_field("description")

    def get_og_site_name(self):
        return self.get_og_field("site_name")

    def get_og_image(self):
        return self.get_og_field("image")

    def get_og_locale(self):
        return self.get_og_field("locale")

    def get_rss_url(self, full_check=False):
        urls = self.get_feeds()
        if urls and len(urls) > 0:
            return urls[0]

    def get_feeds(self):
        if not self.contents:
            return []

        rss_links = self.find_feed_links("application/rss+xml") + self.find_feed_links(
            "application/atom+xml"
        )

        # if not rss_links:
        #    links = self.get_links_inner()
        #    rss_links.extend(
        #        link
        #        for link in links
        #        if "feed" in link or "rss" in link or "atom" in link
        #    )

        return (
            [UrlLocation.get_url_full(self.url, rss_url) for rss_url in rss_links]
            if rss_links
            else []
        )

    def find_feed_links(self, feed_type):
        result_links = []

        found_elements = self.soup.find_all("link")
        for found_element in found_elements:
            if found_element.has_attr("type"):
                link_type = str(found_element["type"])
                if link_type.find(feed_type) >= 0:
                    if found_element.has_attr("href"):
                        result_links.append(found_element["href"])
                    else:
                        WebLogger.error(
                            "Found {} link without href. Str:{}".format(
                                feed_type, str(found_element)
                            )
                        )

        return result_links

    def get_links(self):
        p = ContentLinkParser(self.url, self.contents)
        links = p.get_links()
        links = ContentLinkParser.filter_link_html(links)
        return links

    def get_links_inner(self):
        p = ContentLinkParser(self.url, self.contents)
        return p.get_links_inner()

    def get_links_outer(self):
        p = ContentLinkParser(self.url, self.contents)
        return p.get_links_outer()

    def get_domains(self):
        p = ContentLinkParser(self.url, self.contents)
        return p.get_domains()

    def get_domain_page(self):
        if self.url == self.get_domain():
            return self

        return Page(self.get_domain())

    def get_properties(self):
        props = super().get_properties()

        props["meta_title"] = self.get_title_meta()
        props["meta_description"] = self.get_description_meta()
        props["og_title"] = self.get_og_title()
        props["og_description"] = self.get_og_description()
        props["og_site_name"] = self.get_og_site_name()
        props["og_locale"] = self.get_og_locale()
        props["og_image"] = self.get_og_image()
        # props["is_html"] = self.is_html()
        props["charset"] = self.get_charset()
        props["rss_urls"] = self.get_rss_urls()
        # props["status_code"] = self.status_code

        # if UrlLocation(self.url).is_domain():
        #    if self.is_robots_txt():
        #        props["robots_txt_url"] = UrlLocation(self.url).get_robots_txt_url()
        #        props["site_maps_urls"] = self.get_site_maps()

        props["links"] = self.get_links()
        props["links_inner"] = self.get_links_inner()
        props["links_outer"] = self.get_links_outer()
        props["favicons"] = self.get_favicons()
        props["contents"] = self.get_contents()
        if self.get_contents():
            props["contents_length"] = len(self.get_contents())

        return props

    def get_page_rating_vector(self):
        rating = []

        title_meta = self.get_title_meta()
        title_og = self.get_og_title()
        description_meta = self.get_description_meta()
        description_og = self.get_og_description()
        image_og = self.get_og_image()
        language = self.get_language()

        rating.append(self.get_page_rating_title(title_meta))
        rating.append(self.get_page_rating_title(title_og))
        rating.append(self.get_page_rating_description(description_meta))
        rating.append(self.get_page_rating_description(description_og))
        rating.append(self.get_page_rating_language(language))
        # rating.append(self.get_page_rating_status_code(self.response.status_code))

        if self.get_author() != None:
            rating.append([1, 1])
        if self.get_tags() != None:
            rating.append([1, 1])

        if self.get_date_published() != None:
            rating.append([3, 3])

        if image_og:
            rating.append([5, 5])

        return rating

    def get_page_rating_title(self, title):
        rating = 0
        if title is not None:
            if len(title) > 1000:
                rating += 5
            elif len(title.split(" ")) < 2:
                rating += 5
            elif len(title) < 4:
                rating += 2
            else:
                rating += 10

        return [rating, 10]

    def get_page_rating_description(self, description):
        rating = 0
        if description is not None:
            rating += 5

        return [rating, 5]

    def get_page_rating_language(self, language):
        rating = 0
        if language is not None:
            rating += 5
        if language.find("en") >= 0:
            rating += 1

        return [rating, 5]

    def is_valid(self):
        """
        This is a simple set of rules in which we reject the page:
         - status code
         - if valid HTML code
        """
        if not self.is_contents_html():
            return False

        return True

    def is_contents_html(self):
        """
        We want the checks to be simple yet effective. Check some tokens.

        There can be RSS sources in HTML, HTML inside RSS. Beware
        """
        if not self.contents:
            WebLogger.debug("Could not obtain contents for {}".format(self.url))
            return

        html_tags = self.get_position_of_html_tags()
        rss_tags = self.get_position_of_rss_tags()

        if html_tags >= 0 and rss_tags >= 0:
            return html_tags < rss_tags
        if html_tags >= 0:
            return True

    def get_body_text(self):
        if not self.contents:
            return

        body_find = self.soup.find("body")
        if not body_find:
            return

        return body_find.get_text()

    def get_contents_body_hash(self):
        if not self.contents:
            return

        body = self.get_body_text()

        if body == "":
            return
        elif body:
            return calculate_hash(body)
        else:
            WebLogger.error("HTML: Cannot calculate body hash for:{}".format(self.url))
            if self.contents:
                return calculate_hash(self.contents)

    def is_pwa(self):
        """
        @returns true, if it is progressive web app
        """
        if self.get_pwa_manifest():
            return True

    def get_pwa_manifest(self):
        link_finds = self.soup.find_all("link", attrs={"rel": "manifest"})

        for link_find in link_finds:
            if link_find and link_find.has_attr("href"):
                manifest_path = link_find["href"]

                return manifest_path


class XmlPage(ContentInterface):
    def __init__(self, url, contents):
        super().__init__(url=url, contents=contents)

    def is_valid(self):
        """
        This is a simple set of rules in which we reject the page:
         - status code
         - if valid HTML code
        """
        if not self.is_contents_xml():
            return False

        return True

    def is_contents_xml(self):
        if not self.get_contents():
            return False

        contents = self.get_contents()

        lower = contents.lower()
        if lower.find("<?xml") >= 0:
            return lower.find("<?xml") >= 0


class PageFactory(object):
    def get(response, contents):
        """
        Note: some servers might return text/html for RSS sources.
              We must manually check what kind of data it is.
              For speed - we check first what is suggested by content-type
        """
        contents = None
        if response and response.get_text():
            contents = response.get_text()

        if not contents:
            return

        url = response.request_url

        if response.is_html():
            p = HtmlPage(url, contents)
            if p.is_valid():
                return p

            p = RssPage(url, contents)
            if p.is_valid():
                return p

            p = OpmlPage(url, contents)
            if p.is_valid():
                return p

            p = JsonPage(url, contents)
            if p.is_valid():
                return p

        if response.is_rss():
            p = RssPage(url, contents)
            if p.is_valid():
                return p

            p = OpmlPage(url, contents)
            if p.is_valid():
                return p

            p = HtmlPage(url, contents)
            if p.is_valid():
                return p

            p = JsonPage(url, contents)
            if p.is_valid():
                return p

        if response.is_json():
            p = JsonPage(url, contents)
            if p.is_valid():
                return p

            p = RssPage(url, contents)
            if p.is_valid():
                return p

            p = HtmlPage(url, contents)
            if p.is_valid():
                return p

        if response.is_content_type("image"):
            return
        if response.is_content_type("audio"):
            return
        if response.is_content_type("video"):
            return
        if response.is_content_type("font"):
            return

        # we do not know what it is. Guess

        p = HtmlPage(url, contents)
        if p.is_valid():
            return p

        p = RssPage(url, contents)
        if p.is_valid():
            return p

        p = OpmlPage(url, contents)
        if p.is_valid():
            return p

        p = JsonPage(url, contents)
        if p.is_valid():
            return p

        # TODO
        # p = XmlPage(url, contents)
        # if p.is_valid():
        #    return p

        if response.is_text():
            p = DefaultContentPage(url, contents)
            return p

        p = DefaultContentPage(url, contents)
        return p
