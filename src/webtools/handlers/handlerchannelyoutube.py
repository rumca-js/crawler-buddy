import traceback
from concurrent.futures import ThreadPoolExecutor

from webtoolkit import YouTubeChannelHandler


class YouTubeChannelHandlerJson(YouTubeChannelHandler):
    """
    Natively since we inherit RssPage, the contents should be RssPage
    """

    def __init__(self, url=None, request=None, url_builder=None):
        super().__init__(
            url=url,
            request=request,
            url_builder=url_builder,
        )

    def get_json_data(self):
        entries = self.get_entries()
        for entry in entries:
            u = self.build_default_url(entry["link"])
            handler = u.get_handler()
            json = handler.get_response_json()
            self.social_data["followers_count"] = json.get_followers_count()
            return self.social_data

        return self.social_data

    def get_followers_count(self):
        return self.social_data.get("followers_count")

    def get_social_data(self):
        if len(self.social_data) != 0:
            return super().get_social_data()
