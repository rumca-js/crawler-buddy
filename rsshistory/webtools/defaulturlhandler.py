from .pages import DefaultContentPage
from .handlerinterface import HandlerInterface
from utils.dateutils import DateUtils


class DefaultUrlHandler(HandlerInterface):
    """
    This handler works as HTML page handler, mostly
    """

    def __init__(self, url=None, contents=None, settings=None, url_builder=None):
        super().__init__(url, settings=settings, url_builder=url_builder)

    def get_response(self):
        """
        By default we use HTML response
        """

        if self.response:
            return self.response

        settings = {}
        settings["handler_class"] = HttpPageHandler

        # now call url with those options
        self.handler = self.url_builder(self.url, settings=settings)
        self.response = self.handler.get_response()

        if not self.response or not self.response.is_valid():
            self.dead = True

        if self.response:
            self.contents = self.response.get_text()

            return self.response

    def ping(self, timeout_s=120):
        from .handlerhttppage import HttpPageHandler

        if self.response:
            return self.response

        # now call url with those options
        self.handler = HttpPageHandler(self.url, page_options=self.options)
        status = self.handler.ping(timeout_s)

        return status


class DefaultChannelHandler(DefaultUrlHandler):
    def get_contents(self):
        """
        We obtain information about channel.
        We cannot use HTML page to obtain thumbnail - as web page asks to log in to view this
        """
        if self.dead:
            return

        if self.contents:
            return self.contents

        response = self.get_response()
        if response:
            return self.response.get_text()

    def get_response(self):
        """
        By default we use HTML response
        """
        from .url import Url
        from .handlerhttppage import HttpPageHandler

        if self.response:
            return self.response

        feeds = self.get_feeds()
        if not feeds or len(feeds) == 0:
            self.dead = True
            return

        feed_url = feeds[0]

        settings = {}
        settings["handler_class"] = HttpPageHandler

        # now call url with those options
        self.handler = Url(feed_url, settings=settings)
        self.response = self.handler.get_response()

        if not self.response or not self.response.is_valid():
            self.dead = True

        if self.response:
            self.contents = self.response.get_text()
            return self.response
