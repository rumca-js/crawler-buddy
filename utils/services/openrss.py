from rsshistory.webtools import UrlLocation, HttpPageHandler, RssPage, Url


class OpenRss(object):
    def __init__(self, url):
        self.url = url

    def find_rss_link(self):
        p = UrlLocation(self.url)
        url_procolles = p.get_protocolless()

        u = Url("https://openrss.org/" + url_procolles)
        u.options.mode = "standard"
        u.get_response()

        handler = u.get_handler()
        if type(handler) is HttpPageHandler:
            if type(handler.p) is RssPage:
                return handler.p.get_link()
