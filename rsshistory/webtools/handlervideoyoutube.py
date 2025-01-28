from urllib.parse import urlparse
from urllib.parse import parse_qs

from utils.dateutils import DateUtils

from .webtools import PageResponseObject, WebLogger
from .urllocation import UrlLocation
from .pages import HtmlPage, ContentInterface
from .defaulturlhandler import DefaultUrlHandler


class YouTubeVideoHandler(DefaultUrlHandler):
    def __init__(self, url=None, contents=None, settings=None, url_builder=None):
        super().__init__(
            url, contents=contents, settings=settings, url_builder=url_builder
        )

        self.url = self.input2url(url)
        self.code = self.input2code(url)

    def is_handled_by(self):
        if not self.url:
            return False

        protocol_less = UrlLocation(self.url).get_protocolless()

        return (
            protocol_less.startswith("www.youtube.com/watch")
            or protocol_less.startswith("youtube.com/watch")
            or protocol_less.startswith("m.youtube.com/watch")
            or (
                protocol_less.startswith("youtu.be/")
                and len(protocol_less) > len("youtu.be/")
            )
        )

    def get_video_code(self):
        return self.input2code(self.url)

    def input2url(self, item):
        code = self.input2code(item)
        return self.code2url(code)

    def code2url(self, code):
        if code:
            return "https://www.youtube.com/watch?v={0}".format(code)

    def input2code(self, url):
        if not url:
            return

        if url.find("watch") >= 0 and url.find("v=") >= 0:
            return YouTubeVideoHandler.input2code_standard(url)

        if url.find("youtu.be") >= 0:
            return YouTubeVideoHandler.input2code_youtu_be(url)

    def input2code_youtu_be(url):
        wh = url.find("youtu.be")

        wh_question = url.find("?", wh)
        if wh_question >= 0:
            video_code = url[wh + 9 : wh_question]
        else:
            video_code = url[wh + 9 :]

        return video_code

    def input2code_standard(url):
        parsed_elements = urlparse(url)
        elements = parse_qs(parsed_elements.query)
        if "v" in elements:
            return elements["v"][0]
        else:
            return None

    def get_link_classic(self):
        return "https://www.youtube.com/watch?v={0}".format(self.get_video_code())

    def get_link_mobile(self):
        return "https://www.m.youtube.com/watch?v={0}".format(self.get_video_code())

    def get_link_youtu_be(self):
        return "https://youtu.be/{0}".format(self.get_video_code())

    def get_link_embed(self):
        return "https://www.youtube.com/embed/{0}".format(self.get_video_code())

    def get_link_music(self):
        return "https://music.youtube.com?v={0}".format(self.get_video_code())


class YouTubeHtmlHandler(HtmlPage, YouTubeVideoHandler):
    def __init__(self, url, settings=None):
        super().__init__(url, settings=settings)

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
    TODO Use if above in youtube.h
    """

    def __init__(self, url, settings=None, url_builder=None):
        """
        TODO We should , most probably call the parnet constructor
        """
        super().__init__(url=url, settings=settings, url_builder=url_builder)

        self.yt_text = None
        self.yt_ob = None

        self.rd_text = None
        self.rd_ob = None

        self.return_dislike = False

        self.dead = False
        self.response = None

    def get_contents(self):
        if self.response and self.response.get_text():
            return self.response.get_text()

        if self.dead:
            return

        return self.get_response().get_text()

    def get_response(self):
        if self.response:
            return self.response

        WebLogger.info("YouTube video Handler. Requesting: {}".format(self.url))

        response = PageResponseObject(
            url=self.url, text="", status_code=PageResponseObject.STATUS_CODE_ERROR
        )

        status = False
        if self.download_details():
            if self.load_details():
                response.set_text(self.yt_text, "utf-8")
                response.status_code = PageResponseObject.STATUS_CODE_OK
                response.url = self.get_link_classic()

                status = True
                WebLogger.info("YouTube video handler: {} DONE".format(self.url))
            else:
                WebLogger.error("Url:{} Cannot load youtube details".format(self.url))
        else:
            WebLogger.error("Url:{} Cannot download youtube details".format(self.url))

        self.response = response
        self.contents = self.response.get_text()

        if (
            not self.response
            or self.response.status_code == PageResponseObject.STATUS_CODE_ERROR
        ):
            self.dead = True

        return self.response

    def is_valid(self):
        if self.get_contents():
            status = not self.is_live()
            return status

    def get_title(self):
        if self.get_contents():
            return self.yt_ob.get_title()

    def get_description(self):
        if self.get_contents():
            return self.yt_ob.get_description()

    def get_date_published(self):
        if self.get_contents():
            # TODO use dateutils

            from datetime import date
            from datetime import datetime
            from pytz import timezone

            date_string = self.yt_ob.get_date_published()
            date = datetime.strptime(date_string, "%Y%m%d")
            dt = datetime.combine(date, datetime.min.time())

            dt = DateUtils.to_utc_date(dt)

            return dt

    def get_thumbnail(self):
        if self.get_contents():
            return self.yt_ob.get_thumbnail()

    def get_upload_date(self):
        if self.get_contents():
            return self.yt_ob.get_upload_date()

    def get_view_count(self):
        if self.get_contents():
            return self.rd_ob.get_view_count()

    def get_thumbs_up(self):
        if self.get_contents():
            return self.rd_ob.get_thumbs_up()

    def get_thumbs_down(self):
        if self.get_contents():
            return self.rd_ob.get_thumbs_down()

    def get_channel_code(self):
        if self.get_contents():
            return self.yt_ob.get_channel_code()

    def get_feeds(self):
        result = []
        if self.get_contents():
            return [self.yt_ob.get_channel_feed_url()]

        return result

    def get_channel_name(self):
        if self.get_contents():
            return self.yt_ob.get_channel_name()

    def get_channel_url(self):
        if self.get_contents():
            return self.yt_ob.get_channel_url()

    def get_link_url(self):
        if self.get_contents():
            return self.yt_ob.get_link_url()

    def is_live(self):
        if self.get_contents():
            return self.yt_ob.is_live()
        return False

    def get_author(self):
        if self.get_contents():
            return self.get_channel_name()

    def get_album(self):
        return None

    def get_json_text(self):
        if self.get_contents():
            return self.yt_ob.get_json_data()

    def get_tags(self):
        if self.get_contents():
            return self.yt_ob.get_tags()

    def get_properties(self):
        if not self.get_contents():
            return {}

        youtube_props = super().get_properties()

        yt_json = self.yt_ob._json

        if yt_json:
            if "webpage_url" in yt_json:
                youtube_props["webpage_url"] = yt_json["webpage_url"]
            if "uploader_url" in yt_json:
                youtube_props["uploader_url"] = yt_json["uploader_url"]
            youtube_props["channel_id"] = self.yt_ob.get_channel_code()
            youtube_props["channel"] = self.yt_ob.get_channel_name()
            youtube_props["channel_url"] = self.yt_ob.get_channel_url()
            if "channel_follower_count" in yt_json:
                youtube_props["channel_follower_count"] = yt_json[
                    "channel_follower_count"
                ]
            youtube_props["view_count"] = self.yt_ob.get_view_count()
            youtube_props["like_count"] = self.yt_ob.get_thumbs_up()
            if "duration_string" in yt_json:
                youtube_props["duration"] = yt_json["duration_string"]

        youtube_props["embed_url"] = self.get_link_embed()
        youtube_props["valid"] = self.is_valid()
        feeds = self.get_feeds()
        if len(feeds) > 0:
            youtube_props["channel_feed_url"] = feeds[0]
        youtube_props["contents"] = self.get_json_text()
        youtube_props["keywords"] = self.get_tags()
        youtube_props["live"] = self.is_live()

        return youtube_props

    def load_details(self):
        from utils.serializers import YouTubeJson

        self.yt_ob = YouTubeJson()

        if self.yt_text and not self.yt_ob.loads(self.yt_text):
            return False

        if self.return_dislike:
            from utils.serializers import ReturnDislike

            self.rd_ob = ReturnDislike(self.get_video_code())
            if self.rd_text and not self.rd_ob.loads(self.rd_text):
                return False

        return True

    def download_details(self):
        if not self.download_details_youtube():
            return False
        if not self.download_details_return_dislike():
            return False

        return True

    def download_details_youtube(self):
        if self.yt_text is not None:
            return True

        from utils.programwrappers import ytdlp

        yt = ytdlp.YTDLP(self.url)
        self.yt_text = yt.download_data()
        if self.yt_text is None:
            return False
        return True

    def download_details_return_dislike(self):
        if not self.return_dislike:
            return True

        if self.rd_text is not None:
            return True

        from utils.serializers import ReturnDislike

        self.rd_ob = ReturnDislike(self.get_video_code())
        if self.rd_text and not self.rd_ob.loads(self.rd_text):
            return False

        return True

    def get_thumbnail(self):
        if self.get_contents():
            return self.yt_ob.get_thumbnail()

    def get_upload_date(self):
        if self.get_contents():
            return self.yt_ob.get_upload_date()

    def is_rss(self, fast_check=True):
        return False

    def is_html(self, fast_check=True):
        return False

    def get_view_count(self):
        if self.get_contents():
            return self.rd_ob.get_view_count()

    def get_thumbs_up(self):
        if self.get_contents():
            return self.rd_ob.get_thumbs_up()

    def get_thumbs_down(self):
        if self.get_contents():
            return self.rd_ob.get_thumbs_down()

    def get_channel_code(self):
        if self.get_contents():
            return self.yt_ob.get_channel_code()

    def get_feeds(self):
        result = []
        if self.get_contents():
            return [self.yt_ob.get_channel_feed_url()]

        return result

    def get_channel_name(self):
        if self.get_contents():
            return self.yt_ob.get_channel_name()

    def get_link_url(self):
        if self.get_contents():
            return self.yt_ob.get_link_url()

    def is_live(self):
        if self.get_contents():
            return self.yt_ob.is_live()
        return True

    def get_author(self):
        if self.get_contents():
            return self.get_channel_name()

    def get_album(self):
        return None

    def get_json_text(self):
        if self.get_contents():
            return self.yt_ob.get_json_data()

    def get_tags(self):
        if self.get_contents():
            return self.yt_ob.get_tags()
