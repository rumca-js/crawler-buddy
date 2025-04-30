from utils.dateutils import DateUtils

from .pages import DefaultContentPage
from .handlerinterface import HandlerInterface
from .handlerhttppage import HttpPageHandler


class DefaultUrlHandler(HttpPageHandler):
    """
    This handler works as HTML page handler, mostly
    """

    def __init__(self, url=None, contents=None, settings=None, url_builder=None):
        super().__init__(url, settings=settings, url_builder=url_builder)


class DefaultChannelHandler(DefaultUrlHandler):
    pass
