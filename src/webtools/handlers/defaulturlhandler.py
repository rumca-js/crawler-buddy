from utils.dateutils import DateUtils

from webtoolkit import DefaultContentPage

from .handlerhttppage import HttpPageHandler


class DefaultUrlHandler(HttpPageHandler):
    """
    This handler works as HTML page handler, mostly
    """

    def __init__(self, url=None, contents=None, settings=None, url_builder=None):
        super().__init__(url, settings=settings, url_builder=url_builder)
        self.code = self.input2code(url)

    def get_page_url(self, url, crawler_name=None):
        settings = {}
        settings["handler_class"] = HttpPageHandler

        if crawler_name:
            settings["name"] = crawler_name

        url = self.url_builder(url=url, settings=settings)
        return url


class DefaultChannelHandler(DefaultUrlHandler):
    pass
