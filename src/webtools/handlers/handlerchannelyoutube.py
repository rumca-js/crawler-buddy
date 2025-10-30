import copy

from webtoolkit import PageResponseObject
from webtoolkit import UrlLocation, RssPage
from webtoolkit import WebLogger, DefaultChannelHandler, YouTubeChannelHandler
from webtoolkit import HttpPageHandler


class YouTubeChannelHandlerYdlp(YouTubeChannelHandler):
    """
    Natively since we inherit RssPage, the contents should be RssPage
    """

    def input2code_handle(self, url):
        from utils.programwrappers import ytdlp

        yt = ytdlp.YTDLP(url)
        self.yt_text = yt.download_data()

        if self.yt_text is None:
            WebLogger.error("Cannot obtain text data for url:{}".format(url))
            return

        from utils.serializers import YouTubeJson

        self.yt_ob = YouTubeJson()
        if not self.yt_ob.loads(self.yt_text):
            WebLogger.error(
                "Cannot obtain read json data url:{}\ndata:{}".format(url, self.yt_text)
            )
            return

        return self.yt_ob.get_channel_code()
