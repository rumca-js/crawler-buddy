import logging
import json


class ReturnDislike(object):
    def __init__(self, video_code=None):
        self._video_code = video_code
        self.process()

    def process(self):
        data = self.read_data()
        self.loads(data)

    def read_data(self):
        from ..pluginurl import UrlHandler

        url = "https://returnyoutubedislikeapi.com/votes?videoId=" + self._video_code

        u = UrlHandler(url)
        data = u.get_contents()
        return data

    def loads(self, data):
        try:
            self._json = json.loads(data)
            return self._json
        except ValueError as E:
            logging.critical(E, exc_info=True)
            self._json = {}

    def get_json(self):
        return self._json

    def get_thumbs_up(self):
        return self._json["likes"]

    def get_thumbs_down(self):
        return self._json["dislikes"]

    def get_view_count(self):
        return self._json["viewCount"]

    def get_rating(self):
        return self._json["rating"]
