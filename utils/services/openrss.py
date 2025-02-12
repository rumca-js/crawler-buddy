from src.webtools import UrlLocation, Url


class OpenRss(object):
    def __init__(self, url):
        self.url = url

    def find_rss_link(self):
        p = UrlLocation(self.url)
        url_procolles = p.get_protocolless()

        u = Url("https://openrss.org/" + url_procolles)
        u.get_response()

        properties = u.get_properties()
        if properties:
            return properties["link"]
