from .defaulturlhandler import DefaultChannelHandler
from .urllocation import UrlLocation
from .handlerhttppage import HttpPageHandler


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
            self.url = self.code2url(self.code)

    def is_handled_by(self):
        if not self.url:
            return False

        short_url = UrlLocation(self.url).get_protocolless()

        if short_url.startswith("odysee.com/@"):
            return True
        if short_url.startswith("odysee.com/$/rss"):
            return True

    def input2url(self, item):
        code = self.input2code(item)
        return self.code2url(code)

    def code2url(self, code):
        return "https://odysee.com/{}".format(code)

    def code2feed(self, code):
        return "https://odysee.com/$/rss/{}".format(code)

    def is_channel_name(self):
        short_url = UrlLocation(self.url).get_protocolless()

        if short_url.startswith("odysee.com/@"):
            return True

    def input2code(self, url):
        wh = url.find("odysee.com")
        if wh == -1:
            return url

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

    def get_feeds(self):
        result = []
        if self.code:
            result.append(self.code2feed(self.code))
            return result
        else:
            return []
