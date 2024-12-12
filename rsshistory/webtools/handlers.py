from .defaulturlhandler import DefaultUrlHandler, DefaultChannelHandler
from .urllocation import UrlLocation
from .pages import RssPage


class RedditChannelHandler(DefaultChannelHandler):
    def __init__(self, url=None, contents=None):
        self.html = None  # channel html page contains useful info

        super().__init__(
            url,
            contents=contents,
        )

        if url:
            self.code = self.input2code(url)

    def is_handled_by(self):
        if not self.url:
            return False

        code = self.input2code(self.url)
        if code:
            return True

    def input2code(self, input_string):
        p = UrlLocation(input_string)
        if p.get_domain_only().find("reddit.com") >= 0:
            parts = p.split()
            if len(parts) >= 4 and parts[3] == "r":
                return parts[4]

    def code2feed(self, code):
        return "https://www.reddit.com/r/{}/.rss".format(code)
