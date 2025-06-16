import os
import json
import logging
from datetime import datetime


class YouTubeJson(object):
    def __init__(self, url=None):
        self._json = {}
        self.url = url

    def get_json_data(self):
        return json.dumps(self._json)

    def is_valid(self):
        return self._json != {}

    def get_json(self):
        return self._json

    def loads(self, data):
        try:
            self._json = json.loads(data)
            return self._json
        except ValueError as E:
            logging.critical(E, exc_info=True)

    def write(self, file_name, force=True):
        file_dir = os.path.split(file_name)[0]

        if not os.path.isdir(file_dir):
            os.makedirs(file_dir)

        with open(file_name, "w", encoding="utf-8") as fh:
            fh.write(self.get_json_data())

    def read(self, file_name):
        if not os.path.isfile(file_name):
            return None

        with open(file_name, "r", encoding="utf-8") as fh:
            data = fh.read()
            self.loads(data)

    def is_valid(self):
        if "title" in self._json and "t_likes" in self._json:
            return True
        else:
            return False

    def get_file_name(self):
        if len(self._json) > 0:
            return self._json["_filename"]

    def get_duration(self):
        if len(self._json) > 0:
            return self._json["duration"]

    def get_link(self):
        if len(self._json) > 0:
            return self._json["url"]

    def get_title(self):
        if len(self._json) > 0:
            return self._json["title"]

    def get_thumbnail(self):
        if len(self._json) > 0:
            if "thumbnail" in self._json:
                return self._json["thumbnail"]
            else:
                if "thumbnails" in self._json:
                    return self._json["thumbnails"][0]["url"]

    def get_stretched_ratio(self):
        if len(self._json) > 0:
            return self._json["stretched_ratio"]

    def get_tags(self):
        if len(self._json) > 0:
            if "tags" in self._json:
                return self._json["tags"]

    def get_categories(self):
        if len(self._json) > 0:
            return self._json["categories"]

    def get_channel_name(self):
        if len(self._json) > 0:
            return self._json["channel"]

    def get_date_published(self):
        if len(self._json) > 0:
            if "upload_date" in self._json:
                return self._json["upload_date"]
            if "epoch" in self._json:
                epoch = self._json["epoch"]
                if epoch:
                    date_utc = datetime.utcfromtimestamp(epoch)
                    if date_utc:
                        return date_utc
            if "timestamp" in self._json:
                return self._json["timestamp"]

    def get_channel_url(self):
        if len(self._json) > 0:
            return self._json["channel_url"]

    def get_description(self):
        if len(self._json) > 0:
            return self._json["description"]

    def get_video_length(self):
        if len(self._json) > 0:
            return int(self._json["duration"])

    def get_chapters(self):
        # chapter => end_time, start_time, title
        if len(self._json) > 0:
            if "chapters" in self._json:
                return self._json["chapters"]

    def get_channel_name(self):
        if len(self._json) > 0:
            return self._json["channel"]

    def get_channel_code(self):
        if len(self._json) > 0:
            return self._json["channel_id"]

    def get_channel_url(self):
        if len(self._json) > 0:
            return self._json["channel_url"]

    def get_channel_feed_url(self):
        if len(self._json) > 0:
            return "https://www.youtube.com/feeds/videos.xml?channel_id={}".format(
                self.get_channel_code()
            )

    def get_view_count(self):
        if len(self._json) > 0:
            if "view_count" in self._json:
                return str(self._json["view_count"])
            else:
                print("No view_count in self._json {}".format(self._json))

            # return self._json["t_view_count"]
        return 0

    def get_thumbs_up(self):
        if len(self._json) > 0:
            if "like_count" in self._json:
                return str(self._json["like_count"])
            else:
                print("No like_count in self._json {}".format(self._json))
            # return self._json["t_likes"]

        return 0

    def get_thumbs_down(self):
        if len(self._json) > 0:
            return self._json["t_dislikes"]

    def get_rating(self):
        if len(self._json) > 0:
            return self._json["t_rating"]

    def get_upload_date(self):
        if len(self._json) > 0:
            return self._json["upload_date"]

    def is_live(self):
        if len(self._json) > 0:
            is_live = False
            if "live_status" in self._json:
                not_alive = (
                    self._json["live_status"] == "not_live"
                    or self._json["live_status"] == "False"
                )

                is_live = not not_alive

            was_live = False
            if "was_live" in self._json:
                was_live = self._json["was_live"]

            return is_live or was_live
        return False

    def get_link_url(self):
        if len(self._json) > 0:
            return "https://www.youtube.com/watch?v={}".format(self._json["id"])

    def add_return_dislike_data(self, rdd):
        self._json["t_likes"] = rdd.get_likes()
        self._json["t_dislikes"] = rdd.get_dislikes()
        self._json["t_view_count"] = rdd.get_view_count()
        self._json["t_rating"] = rdd.get_rating()
