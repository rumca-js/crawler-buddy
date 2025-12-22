"""
Handles YouTube video contents

Provided because we have yt-dlp crawler now.
"""
from datetime import date
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

from urllib.parse import urlparse
from urllib.parse import parse_qs
from concurrent.futures import ThreadPoolExecutor

from utils.dateutils import DateUtils
from utils.serializers import YouTubeJson
from utils.programwrappers import ytdlp

from webtoolkit import PageResponseObject, UrlLocation, HtmlPage, ContentInterface
from webtoolkit import WebLogger
from webtoolkit import DefaultUrlHandler, YouTubeVideoHandler, HandlerInterface


class YouTubeVideoHandlerJson(YouTubeVideoHandler):
    """
    YouTube JSON enabled video handler.
    TODO Rename to YouTubeVideoHandlerYtdlp
    """

    def __init__(self, url, request=None, url_builder=None):
        """
        Constructor
        """
        super().__init__(url=url, request=request, url_builder=url_builder)

        self.social_data = None

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

    def get_channel_sources(self):
        sources = []
        sources.append(self.url)

        return sources

    def is_valid(self) -> bool:
        """
        Returns indication if is valid
        """
        if self.response:
            status = not self.is_live()
            return status
        return False

    def get_title(self) -> str | None:
        """
        Returns title
        """
        title = super().get_title()
        if title is None:
            if self.yt_ob:
                return self.yt_ob.get_title()
        else:
            return title

    def get_description(self) -> str | None:
        """
        Returns description
        """
        description = super().get_description()
        if description is None:
            if self.yt_ob:
                return self.yt_ob.get_description()
        return description

    def get_date_published(self):
        """
        Returns date published
        """
        date_published = super().get_date_published()
        if date_published is not None:
            return date_published

        if self.yt_ob:
            date_string = self.yt_ob.get_date_published()
            date = datetime.strptime(date_string, "%Y%m%d")
            dt = datetime.combine(date, datetime.min.time())

            dt = DateUtils.to_utc_date(dt)

            return dt

    def get_thumbnail(self):
        """
        Returns thumbnail
        """
        thumbnail = super().get_thumbnail()
        if thumbnail is not None:
            return thumbnail

        if self.yt_ob:
            return self.yt_ob.get_thumbnail()

    def get_author(self):
        """
        Returns author
        """
        if self.yt_ob:
            return self.get_channel_name()

    def get_album(self):
        """
        Returns album
        """
        return None

    def get_upload_date(self):
        """
        Returns upload date
        """
        if self.yt_ob:
            return self.yt_ob.get_upload_date()

    def get_channel_code(self):
        """
        Returns channel code
        """
        if self.yt_ob:
            return self.yt_ob.get_channel_code()

    def get_feeds(self):
        """
        Returns feeds
        """
        result = []
        if self.yt_ob:
            return [self.yt_ob.get_channel_feed_url()]

        return result

    def get_channel_name(self):
        """
        Returns channel name
        """
        if self.yt_ob:
            return self.yt_ob.get_channel_name()

    def get_channel_url(self):
        """
        Returns channel url
        """
        if self.yt_ob:
            return self.yt_ob.get_channel_url()

    def get_link_url(self):
        if self.yt_ob:
            return self.yt_ob.get_link_url()

    def is_live(self):
        """
        Returns indication if video is live
        """
        if self.yt_ob:
            return self.yt_ob.is_live()
        return False

    def get_json_text(self):
        if self.yt_ob:
            return self.yt_ob.get_json_data()

    def get_social_data(self):
        """
        Returns social data map. View counts, thumbs ups, stars, followers counts, etc..
        """
        if self.social_data is None:
            self.get_json_data()

        return HandlerInterface.get_social_data(self)

    def get_json_data(self):
        if self.social_data != None:
            return self.social_data

        self.social_data = {}

        with ThreadPoolExecutor() as executor:
            handle_rd = executor.submit(self.get_json_data_from_rd)
            handle_yt = executor.submit(self.get_json_data_from_yt)

            rd_social = handle_rd.result()
            yt_social = handle_yt.result()

            if rd_social:
                self.social_data = rd_social
            elif yt_social:
                self.social_data = yt_social

            if yt_social:
                for key, value in yt_social.items():
                    self.social_data.setdefault(key, value)

        return self.social_data

    def get_yt_json_url(self):
        if self.json_url:
            return self.json_url
        
        url = self.get_link_classic()

        self.json_url = self.get_page_url(url = url, crawler_name="YtdlpCrawler")
        return self.json_url

    def get_rd_json_url(self):
        request_url = self.get_return_dislike_url_link()

        self.return_url = self.build_default_url(url = request_url)
        return self.return_url

    def get_json_data_from_yt(self):
        """
        Returns social data captured from YouTube JSON
        """
        json_data = {}

        if not self.yt_ob:
            self.get_response_yt_json()
        if self.yt_ob is None:
            WebLogger.error("Url:{}:Could not download youtube details".format(self.url))
            return

        view_count = None
        thumbs_up = None
        thumbs_down = None
        followers_count = None

        try:
            view_count = int(self.yt_ob.get_view_count())
        except TypeError as E:
            pass
        except ValueError as E:
            pass
        except AttributeError as E:
            pass
        json_data["view_count"] = view_count

        try:
            thumbs_up = int(self.yt_ob.get_thumbs_up())
        except TypeError as E:
            pass
        except ValueError as E:
            pass
        except AttributeError as E:
            pass
        json_data["thumbs_up"] = thumbs_up

        try:
            followers_count = int(self.yt_ob.get_followers_count())
        except TypeError as E:
            pass
        except ValueError as E:
            pass
        except AttributeError as E:
            pass
        json_data["followers_count"] = followers_count

        return json_data

    def get_json_data_from_rd(self):
        """
        Returns social data captured from YouTube return dislike page
        """
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
        """
        Returns properties
        """
        if not self.get_response():
            return {}

        youtube_props = super().get_properties(self)

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
        """
        Returns streams
        """
        if self.html_url is not None:
            self.streams[self.html_url.get_url()] = (
                self.html_url.get_response()
            )  # TODO this should be response object
        if self.return_url is not None:
            self.streams[self.return_url.get_url()] = (
                self.return_url.get_response()
            )  # TODO this should be response object

        for key in self.channel_sources_urls:
            self.streams[key] = self.channel_sources_urls[key].get_response()

        return self.streams

    def get_response_yt_json(self):
        if self.yt_ob is not None:
            return self.yt_ob

        url = self.get_yt_json_url()
        response = url.get_response()
        if response is None:
            WebLogger.debug("Url:{} No response".format(url.get_url()))
            return

        if not response.is_valid():
            WebLogger.debug("Url:{} response is not valid".format(url.get_url()))
            return

        self.yt_text = response.get_text()
        if not self.yt_text:
            WebLogger.debug("Url:{} response no text".format(url.get_url()))
            return

        return self.load_details_youtube()

    def get_return_dislike_url_link(self):
        return "https://returnyoutubedislikeapi.com/votes?videoId=" + self.get_video_code()

    def get_response_return_dislike(self):
        if self.rd_text is not None:
            return True

        url = self.get_rd_json_url()
        response = url.get_response()
        if response is None:
            WebLogger.debug("Url:{} No response".format(url.get_url()))
            return False

        if not response.is_valid():
            WebLogger.debug("Url:{} response is not valid".format(url.get_url()))
            return False

        self.rd_text = response.get_text()
        if not self.rd_text:
            WebLogger.debug("Url:{} response no text".format(url.get_url()))
            return False
        handler = self.return_url.get_handler()

        handler.load_response()
        self.rd_ob = handler

        if not self.rd_ob:
            return False

        return True

    def get_view_count(self):
        """
        Returns view count
        """
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
        """
        Returns thumbs up
        """
        if self.social_data:
            return self.social_data.get("thumbs_up")

    def get_thumbs_down(self):
        """
        Returns thumbs down
        """
        if self.social_data:
            return self.social_data.get("thumbs_down")

    def get_followers_count(self):
        """
        Returns followers count
        """
        if self.social_data:
            return self.social_data.get("followers_count")

    def get_view_count(self):
        """
        Returns view count
        """
        if self.social_data:
            return self.social_data.get("view_count")

    def get_rating(self):
        """
        Returns rating
        """
        if self.social_data:
            return self.social_data.get("rating")
