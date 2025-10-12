from webtoolkit import UrlLocation
from webtoolkit import WebLogger

from .handlerhttppage import HttpPageHandler
from .defaulturlhandler import DefaultChannelHandler


class OdyseeChannelHandler(DefaultChannelHandler):

    def __init__(self, url=None, contents=None, settings=None, url_builder=None):
        super().__init__(
            url,
            contents=contents,
            settings=settings,
            url_builder=url_builder,
        )

        if url:
            self.code = self.input2code(url)

        self.rss_url = None

    def is_handled_by(self):
        if not self.url:
            return False

        short_url = UrlLocation(self.url).get_protocolless()

        if short_url.startswith("odysee.com/@"):
            return True
        elif short_url.startswith("odysee.com/$/rss"):
            return True

    def input2url(self, item):
        code = self.input2code(item)
        return self.code2url(code)

    def code2url(self, code):
        return "https://odysee.com/{}".format(code)

    def code2feed(self, code):
        return "https://odysee.com/$/rss/{}".format(code)

    def get_feeds(self):
        feeds = super().get_feeds()
        if self.code:
            feeds.append("https://odysee.com/$/rss/{}".format(self.code))

        return feeds

    def is_channel_name(self):
        short_url = UrlLocation(self.url).get_protocolless()

        if short_url.startswith("odysee.com/@"):
            return True

    def input2code(self, url):
        wh = url.find("odysee.com")
        if wh == -1:
            return None

        if url.find("https://odysee.com/$/rss/") >= 0:
            return self.input2code_feeds(url)
        if url.find("https://odysee.com/") >= 0:
            return self.input2code_channel(url)

    def input2code_channel(self, url):
        if not self.url:
            return False

        short_url = UrlLocation(self.url).get_protocolless()
        lines = short_url.split("/")
        if len(lines) < 2:
            return

        base = lines[0]  # odysee.com
        code = lines[1]

        wh = code.find("?")
        if wh >= 0:
            code = code[:wh]

        return code

    def input2code_feeds(self, url):
        if not self.url:
            return False

        short_url = UrlLocation(self.url).get_protocolless()
        lines = short_url.split("/")
        if len(lines) < 2:
            return

        base = lines[0]  # odysee.com
        dollar = lines[1]  # $
        rss = lines[2]  # rss
        code = lines[3]

        wh = code.find("?")
        if wh >= 0:
            code = code[:wh]

        return code

    def get_channel_code(self):
        return self.code

    def get_channel_url(self):
        return self.code2url(self.code)

    def get_channel_feed(self):
        return self.code2feed(self.code)

    def get_entries(self):
        rss_url = self.get_rss_url()
        if rss_url:
            return rss_url.get_entries()
        else:
            return []

    def get_rss_url(self):

        if self.rss_url:
            return self.rss_url

        feeds = self.get_feeds()
        if not feeds or len(feeds) == 0:
            WebLogger.error(
                "Url:{} Cannot read YouTube channel feed URL".format(self.url)
            )
            return

        feed = feeds[0]

        if not feed:
            return

        settings = {}
        settings["handler_class"] = HttpPageHandler

        self.rss_url = self.url_builder(feed, settings=settings)
        self.rss_url.get_response()
        return self.rss_url
