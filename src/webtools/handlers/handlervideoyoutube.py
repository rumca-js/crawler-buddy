from urllib.parse import urlparse
from urllib.parse import parse_qs

from utils.dateutils import DateUtils

from webtoolkit import PageResponseObject, UrlLocation, HtmlPage, ContentInterface
from webtoolkit import WebLogger

from .defaulturlhandler import DefaultUrlHandler


class YouTubeVideoHandler(DefaultUrlHandler):
    def __init__(self, url=None, contents=None, settings=None, url_builder=None):
        super().__init__(
            url, contents=contents, settings=settings, url_builder=url_builder
        )

        if not self.is_handled_by():
            return

        self.code = self.input2code(url)

    def is_handled_by(self):
        if not self.url:
            return False

        protocol_less = UrlLocation(self.url).get_protocolless()

        return (
            self.is_handled_by_watch(protocol_less)
            or self.is_handled_by_shorts(protocol_less)
            or self.is_handled_by_be_domain(protocol_less)
        )

    def is_handled_by_watch(self, protocol_less):
        return (
            protocol_less.startswith("www.youtube.com/watch")
            or protocol_less.startswith("youtube.com/watch")
            or protocol_less.startswith("m.youtube.com/watch")
        )

    def get_canonical_url(self):
        return self.code2url(self.code)

    def is_handled_by_shorts(self, protocol_less):
        return (
            protocol_less.startswith("www.youtube.com/shorts")
            or protocol_less.startswith("youtube.com/shorts")
            or protocol_less.startswith("m.youtube.com/shorts")
        )

    def is_handled_by_be_domain(self, protocol_less):
        return protocol_less.startswith("youtu.be/") and len(protocol_less) > len(
            "youtu.be/"
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

        if url.find("shorts") >= 0:
            return YouTubeVideoHandler.input2code_shorts(url)

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

    def input2code_shorts(url):
        wh = url.find("shorts")

        wh_question = url.find("?", wh)
        if wh_question >= 0:
            video_code = url[wh + 7 : wh_question]
        else:
            video_code = url[wh + 7 :]

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

        self.social_data = {}
        self.yt_text = None
        self.yt_ob = None

        self.rd_text = None
        self.rd_ob = None

        self.return_dislike = True

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
            response.set_text(self.yt_text, "utf-8")
            response.status_code = PageResponseObject.STATUS_CODE_OK
            response.url = self.get_link_classic()

            status = True

            WebLogger.info("YouTube video handler: {} DONE".format(self.url))
        else:
            WebLogger.error("Url:{} Cannot download youtube details".format(self.url))

        self.response = response
        self.contents = self.response.get_text()

        self.social_data = self.get_json_data()

        if (
            not self.response
            or self.response.status_code == PageResponseObject.STATUS_CODE_ERROR
        ):
            self.dead = True

        return self.response

    def is_valid(self):
        if self.response:
            status = not self.is_live()
            return status

    def get_title(self):
        if self.yt_ob:
            return self.yt_ob.get_title()

    def get_description(self):
        if self.yt_ob:
            return self.yt_ob.get_description()

    def get_date_published(self):
        if self.yt_ob:
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

        social_data = self.get_json_data_from_yt()
        for key, value in social_data.items():
            self.social_data.setdefault(key, value)

        return self.social_data

    def get_json_data_from_yt(self):
        json_data = {}

        if not self.yt_ob:
            self.download_details_youtube()
        if self.yt_ob is None:
            print("Could not download youtube details")

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
            self.download_details_return_dislike()
        if not self.rd_ob:
            print("Could not download return dislikes youtube details")

        view_count = None
        thumbs_up = None
        thumbs_down = None

        try:
            view_count = int(self.rd_ob.get_view_count())
        except (ValueError, AttributeError) as E:
            pass

        try:
            thumbs_up = int(self.rd_ob.get_thumbs_up())
        except (ValueError, AttributeError) as E:
            pass

        try:
            thumbs_down = int(self.rd_ob.get_thumbs_down())
        except (ValueError, AttributeError) as E:
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
            return True

        from utils.serializers import YouTubeJson

        self.yt_ob = YouTubeJson()

        if self.yt_text and not self.yt_ob.loads(self.yt_text):
            return False

        return True

    def download_details(self):
        if not self.download_details_youtube():
            WebLogger.error("Cannot load youtube details. Is yt-dlp update required?")
            return False

        return True

    def get_streams(self):
        if self.yt_text:
            self.streams["yt-dlp JSON"] = (
                self.yt_text
            )  # TODO this should be response object
        if self.rd_text:
            self.streams["ReturnDislike JSON"] = (
                self.rd_text
            )  # TODO this should be response object

        return self.streams

    def download_details_youtube(self):
        if self.yt_text is not None:
            return True

        from utils.programwrappers import ytdlp

        yt = ytdlp.YTDLP(self.url)
        self.yt_text = yt.download_data()
        if self.yt_text is None:
            return False

        return self.load_details_youtube()

    def download_details_return_dislike(self):
        if self.rd_text is not None:
            return True

        from .handlers import ReturnDislike

        dislike = ReturnDislike(video_code=self.get_video_code())
        dislike.get_response()
        self.rd_text = dislike.get_contents()
        if not self.rd_text:
            return False

        dislike.load_response()
        self.rd_ob = dislike

        if not self.rd_ob:
            return False

        return True

    def get_thumbnail(self):
        if self.yt_ob:
            return self.yt_ob.get_thumbnail()

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
        from utils.programwrappers import ytdlp
        from utils.serializers import YouTubeJson

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
