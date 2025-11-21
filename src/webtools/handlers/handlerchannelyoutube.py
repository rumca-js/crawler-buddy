"""
Provides handling for YouTube channel.

Can read channel followers count.
"""
import traceback

from webtoolkit import YouTubeChannelHandler


class YouTubeChannelHandlerJson(YouTubeChannelHandler):
    """
    YouTube channel handler.
    """

    def __init__(self, url=None, request=None, url_builder=None):
        """
        Constructor
        """
        super().__init__(
            url=url,
            request=request,
            url_builder=url_builder,
        )

    def get_json_data(self):
        self.get_response()
        entries = self.get_entries()
        for entry in entries:
            u = self.build_default_url(entry["link"])
            handler = u.get_handler()
            json = handler.get_response_yt_json()
            self.social_data["followers_count"] = json.get_followers_count()
            return self.social_data

        return self.social_data

    def get_followers_count(self):
        """
        Returns follower count
        """
        return self.social_data.get("followers_count")

    def get_social_data(self):
        if len(self.social_data) == 0:
            self.get_json_data()

        return super().get_social_data()
