from ..urllocation import UrlLocation

from .defaulturlhandler import DefaultUrlHandler


class OdyseeVideoHandler(DefaultUrlHandler):
    def __init__(self, url=None, contents=None, settings=None, url_builder=None):
        super().__init__(
            url, contents=contents, settings=settings, url_builder=url_builder
        )
        self.channel = None
        self.video = None
        self.url = self.input2url(url)

    def is_handled_by(self):
        if not self.url:
            return

        protocol_less = UrlLocation(self.url).get_protocolless()

        if protocol_less.startswith("odysee.com/@"):
            wh1 = protocol_less.find("@")
            wh2 = protocol_less.find("/", wh1 + 1)
            if wh2 >= 0:
                return True
        elif protocol_less.startswith("odysee.com/"):
            # syntax reserved for channel RSS
            # test_link = "https://odysee.com/$/rss/@samtime:0"
            if protocol_less.startswith("odysee.com/$"):
                return False
            return True

    def input2url(self, url):
        protocol_less = UrlLocation(self.url).get_protocolless()

        if protocol_less.startswith("odysee.com/@"):
            return self.handle_channel_video_input(url)
        elif protocol_less.startswith("odysee.com/"):
            return self.handle_video_input(url)

    def handle_channel_video_input(self, url):
        protocol_less = UrlLocation(self.url).get_protocolless()

        lines = protocol_less.split("/")
        if len(lines) < 3:
            return

        first = lines[0]  # odysee.com
        self.channel = lines[1]
        self.video = lines[2]
        wh = self.video.find("?")
        if wh >= 0:
            self.video = self.video[:wh]

        protocol_less = "/".join([first, self.channel, self.video])

        return "https://" + protocol_less

    def handle_video_input(self, url):
        protocol_less = UrlLocation(self.url).get_protocolless()

        lines = protocol_less.split("/")
        if len(lines) < 2:
            return url

        first = lines[0]  # odysee.com
        self.video = lines[1]

        protocol_less = "/".join([first, self.video])

        return "https://" + protocol_less

    def get_video_code(self):
        return self.video

    def get_channel_code(self):
        return self.channel

    def get_link_classic(self):
        if self.get_channel_code():
            return "https://odysee.com/{}/{}".format(
                self.get_channel_code(), self.get_video_code()
            )
        else:
            return "https://odysee.com/{}".format(self.get_video_code())

    def get_link_embed(self):
        return "https://odysee.com/$/embed/{0}".format(self.get_video_code())

    def get_response(self):
        from .handlerhttppage import HttpPageHandler

        if self.response:
            return self.response

        if self.dead:
            return

        settings = {}
        settings["handler_class"] = HttpPageHandler

        self.handler = self.url_builder(self.url, settings=settings)
        self.response = self.handler.get_response()

        if self.response:
            return self.response

    def get_feeds(self):
        from .handlerchannelodysee import OdyseeChannelHandler

        return [OdyseeChannelHandler().code2feed(self.channel)]
