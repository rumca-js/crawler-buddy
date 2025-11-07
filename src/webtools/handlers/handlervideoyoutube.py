from datetime import date
from datetime import datetime

from urllib.parse import urlparse
from urllib.parse import parse_qs
from concurrent.futures import ThreadPoolExecutor

from utils.dateutils import DateUtils
from utils.serializers import YouTubeJson
from utils.programwrappers import ytdlp

from webtoolkit import PageResponseObject, UrlLocation, HtmlPage, ContentInterface
from webtoolkit import WebLogger
from webtoolkit import DefaultUrlHandler, YouTubeVideoHandler


class YouTubeHtmlHandler(YouTubeVideoHandler):
    def __init__(self, url, request=None, url_builder=None):
        super().__init__(url, request=request, url_builder=url_builder)

    def is_valid(self):
        """
        Either use html or JSON.
        """
        if not self.is_youtube():
            return False

        if not super().is_valid():
            return False

        # TODO make this configurable in config
        block_live_videos = True

        # TODO
        # invalid_text = '{"simpleText":"GO TO HOME"}'
        # contents = self.h.get_contents()
        # if contents and contents.find(invalid_text) >= 0:
        #    return False

        if block_live_videos:
            live_field = self.h.get_meta_custom_field("itemprop", "isLiveBroadcast")
            if live_field and live_field.lower() == "true":
                return False

        return True

        if self.is_live():
            return False

        return True


class YouTubeJsonHandler(YouTubeVideoHandler):
    """
    TODO Rename to YouTubeVideoHandlerYtdlp
    """

    def __init__(self, url, request=None, url_builder=None):
        """
        TODO We should , most probably call the parnet constructor
        """
        super().__init__(url=url, request=request, url_builder=url_builder)

        self.social_data = {}

        self.json_url = None
        self.return_url = None
        self.html_url = None

        self.yt_text = None
        self.yt_ob = None

        self.rd_text = None
        self.rd_ob = None

        self.return_dislike = True

        self.dead = False
        self.response = None

    def is_valid(self):
        if self.response:
            status = not self.is_live()
            return status

    def get_title(self):
        if self.html_url:
            return self.html_url.get_title()
        if self.yt_ob:
            return self.yt_ob.get_title()

    def get_description(self):
        if self.html_url:
            return self.html_url.get_description()
        if self.yt_ob:
            return self.yt_ob.get_description()

    def get_date_published(self):
        if self.html_url:
            return self.html_url.get_date_published()

        if self.yt_ob:
            date_string = self.yt_ob.get_date_published()
            date = datetime.strptime(date_string, "%Y%m%d")
            dt = datetime.combine(date, datetime.min.time())

            dt = DateUtils.to_utc_date(dt)

            return dt

    def get_thumbnail(self):
        if self.html_url:
            return self.html_url.get_thumbnail()

        if self.yt_ob:
            return self.yt_ob.get_thumbnail()

    def get_upload_date(self):
        if self.yt_ob:
            return self.yt_ob.get_upload_date()

    def get_view_count(self):
        if self.response:
            view_count = None

            if not view_count:
                if self.yt_ob:
                    view_count = self.yt_ob.get_view_count()
            if not view_count:
                if self.rd_ob:
                    view_count = self.rd_ob.get_view_count()
            return view_count

    def get_thumbs_up(self):
        if self.rd_ob:
            return self.rd_ob.get_thumbs_up()

    def get_thumbs_down(self):
        if self.rd_ob:
            return self.rd_ob.get_thumbs_down()

    def get_channel_code(self):
        if self.yt_ob:
            return self.yt_ob.get_channel_code()

    def get_feeds(self):
        result = []
        if self.yt_ob:
            return [self.yt_ob.get_channel_feed_url()]

        return result

    def get_channel_name(self):
        if self.yt_ob:
            return self.yt_ob.get_channel_name()

    def get_channel_url(self):
        if self.yt_ob:
            return self.yt_ob.get_channel_url()

    def get_link_url(self):
        if self.yt_ob:
            return self.yt_ob.get_link_url()

    def is_live(self):
        if self.yt_ob:
            return self.yt_ob.is_live()
        return False

    def get_author(self):
        if self.yt_ob:
            return self.get_channel_name()

    def get_album(self):
        return None

    def get_json_text(self):
        if self.yt_ob:
            return self.yt_ob.get_json_data()

    def get_json_data(self):
        if self.social_data != {}:
            return self.social_data

        self.social_data = {}

        if self.return_dislike:
            self.social_data = self.get_json_data_from_rd()
            if not self.social_data:
                self.social_data = {}

        social_data = self.get_json_data_from_yt()
        if social_data:
            for key, value in social_data.items():
                self.social_data.setdefault(key, value)

        return self.social_data

    def get_json_data_from_yt(self):
        json_data = {}

        if not self.yt_ob:
            self.get_response_json()
        if self.yt_ob is None:
            WebLogger.error("Url:{}:Could not download youtube details".format(self.url))
            return

        view_count = None
        thumbs_up = None
        thumbs_down = None

        try:
            view_count = int(self.yt_ob.get_view_count())
        except ValueError as E:
            pass
        except AttributeError as E:
            pass

        json_data["view_count"] = view_count
        return json_data

    def get_json_data_from_rd(self):
        json_data = {}

        if not self.rd_ob:
            self.get_response_return_dislike()
        if not self.rd_ob:
            WebLogger.error("Url:{}:Could not download return dislike details".format(self.url))
            return

        view_count = None
        thumbs_up = None
        thumbs_down = None

        try:
            view_count = int(self.rd_ob.get_view_count())
        except (ValueError, AttributeError, TypeError) as E:
            pass

        try:
            thumbs_up = int(self.rd_ob.get_thumbs_up())
        except (ValueError, AttributeError, TypeError) as E:
            pass

        try:
            thumbs_down = int(self.rd_ob.get_thumbs_down())
        except (ValueError, AttributeError, TypeError) as E:
            pass

        json_data["view_count"] = view_count
        json_data["thumbs_up"] = thumbs_up
        json_data["thumbs_down"] = thumbs_down

        return json_data

    def get_tags(self):
        if self.yt_ob:
            return self.yt_ob.get_tags()

    def get_properties(self):
        if not self.get_response():
            return {}

        youtube_props = ContentInterface.get_properties(self)

        yt_json = self.yt_ob._json

        if yt_json:
            youtube_props["webpage_url"] = yt_json.get("webpage_url")
            youtube_props["uploader_url"] = yt_json.get("uploader_url")
            youtube_props["view_count"] = self.yt_ob.get_view_count()
            youtube_props["like_count"] = self.yt_ob.get_thumbs_up()
            youtube_props["duration"] = yt_json.get("duration_string")

            youtube_props["channel_id"] = self.yt_ob.get_channel_code()
            youtube_props["channel"] = self.yt_ob.get_channel_name()
            youtube_props["channel_url"] = self.yt_ob.get_channel_url()
            youtube_props["channel_follower_count"] = self.yt_ob.get_followers_count()

        youtube_props["embed_url"] = self.get_link_embed()
        youtube_props["valid"] = self.is_valid()
        feeds = self.get_feeds()
        if len(feeds) > 0:
            youtube_props["channel_feed_url"] = feeds[0]
        youtube_props["contents"] = self.get_json_text()
        youtube_props["keywords"] = self.get_tags()
        youtube_props["live"] = self.is_live()

        return youtube_props

    def load_details_youtube(self):
        if self.yt_ob is not None:
            return self.yt_ob

        self.yt_ob = YouTubeJson()

        if self.yt_text and not self.yt_ob.loads(self.yt_text):
            return

        return self.yt_ob

    def get_streams(self):
        if self.html_url is not None:
            self.streams["HTML"] = (
                self.html_url.get_response()
            )  # TODO this should be response object
        if self.return_url is not None:
            self.streams["ReturnDislike JSON"] = (
                self.return_url.get_response()
            )  # TODO this should be response object

        return self.streams

    def get_response_json(self):
        if self.yt_text is not None:
            return True

        self.json_url = self.get_page_url(url = self.url, crawler_name="YtdlpCrawler")
        response = self.json_url.get_response()
        if response is None:
            WebLogger.debug("Url:{} No response".format(url))
            return False

        if not response.is_valid():
            WebLogger.debug("Url:{} response is not valid".format(url))
            return False

        self.yt_text = response.get_text()
        if not self.yt_text:
            WebLogger.debug("Url:{} response no text".format(url))
            return False

        return self.load_details_youtube()

    def get_return_dislike_url_link(self):
        return "https://returnyoutubedislikeapi.com/votes?videoId=" + self.get_video_code()

    def get_response_return_dislike(self):
        if self.rd_text is not None:
            return True

        request_url = self.get_return_dislike_url_link()

        self.return_url = self.build_default_url(url = request_url)
        response = self.return_url.get_response()
        if response is None:
            WebLogger.debug("Url:{} No response".format(url))
            return False

        if not response.is_valid():
            WebLogger.debug("Url:{} response is not valid".format(url))
            return False

        self.rd_text = response.get_text()
        if not self.rd_text:
            WebLogger.debug("Url:{} response no text".format(url))
            return False
        handler = self.return_url.get_handler()

        handler.load_response()
        self.rd_ob = handler

        if not self.rd_ob:
            return False

        return True

    def get_upload_date(self):
        if self.yt_ob:
            return self.yt_ob.get_upload_date()

    def is_rss(self, fast_check=True):
        return False

    def is_html(self, fast_check=True):
        return False

    def get_view_count(self):
        if self.response:
            view_count = None

            if not view_count and self.rd_ob:
                view_count = self.rd_ob.get_view_count()

            if not view_count and self.yt_ob:
                view_count = self.yt_ob.get_view_count()

            return view_count

    def get_thumbs_up(self):
        if self.rd_ob:
            return self.rd_ob.get_thumbs_up()

    def get_thumbs_down(self):
        if self.rd_ob:
            return self.rd_ob.get_thumbs_down()

    def get_followers_count(self):
        if self.yt_ob:
            return self.yt_ob.get_followers_count()

    def get_channel_code(self):
        if self.yt_ob:
            return self.yt_ob.get_channel_code()

    def get_view_count(self):
        if self.rd_ob:
            return self.rd_ob.get_view_count()
        if self.yt_ob:
            return self.yt_ob.get_view_count()

    def get_feeds(self):
        result = []
        if self.yt_ob:
            return [self.yt_ob.get_channel_feed_url()]

        return result

    def get_channel_name(self):
        if self.yt_ob:
            return self.yt_ob.get_channel_name()

    def get_link_url(self):
        if self.yt_ob:
            return self.yt_ob.get_link_url()

    def is_live(self):
        if self.yt_ob:
            return self.yt_ob.is_live()
        return True

    def get_author(self):
        if self.yt_ob:
            return self.get_channel_name()

    def get_album(self):
        return None

    def get_json_text(self):
        if self.yt_ob:
            return self.yt_ob.get_json_data()

    def get_tags(self):
        if self.yt_ob:
            return self.yt_ob.get_tags()

    def get_entries(self):
        entries = []

        location = UrlLocation(self.url)
        params = location.get_params()

        if params and "list" in params:
            yt = ytdlp.YTDLP(self.url)
            json = yt.get_video_list_json()

            if not json:
                return entries

            for video in json:
                j = YouTubeJson()
                j._json = video

                if "url" in video and video["url"] is not None:
                    url = j.get_link()
                    title = j.get_title()
                    description = j.get_description()
                    channel_url = j.get_channel_url()
                    date_published = j.get_date_published()
                    view_count = j.get_view_count()
                    live_status = j.is_live()
                    thumbnail = j.get_thumbnail()

                    entry_data = {
                        "link": url,
                        "title": title,
                        "description": description,
                        "date_published": date_published,
                        "thumbnail": thumbnail,
                        "live": live_status,
                        "view_count": view_count,
                        "channel_url": channel_url,
                        "source_url": channel_url,
                    }

                    entries.append(entry_data)

        return entries
