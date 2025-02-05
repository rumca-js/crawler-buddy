import json

from .defaulturlhandler import DefaultUrlHandler, DefaultChannelHandler
from .urllocation import UrlLocation
from .pages import RssPage
from .webtools import (
    WebLogger,
)


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


class RedditUrlHandler(DefaultUrlHandler):
    """https://www.reddit.com/r/redditdev/comments/1hw8p3j/i_used_the_reddit_api_to_save_myself_time_with_my/"""

    """https://www.reddit.com/r/redditdev/comments/1hw8p3j/i_used_the_reddit_api_to_save_myself_time_with_my/.json"""

    def __init__(self, url=None, contents=None):
        super().__init__(
            url,
            contents=contents,
        )

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
            if len(parts) >= 6 and parts[3] == "r" and parts[5] == "comments":
                subreddit = parts[4]
                post_id = parts[6]

                return post_id

    def get_json_url(self):
        post_id = self.input2code(self.url)
        if post_id:
            return f"https://www.reddit.com/{post_id}.json"
        else:
            WebLogger.error("Reddit:did not found post id {}".format(self.url))

    def get_json_text(self):
        """
        This function loads reddit comment JSON.
        We cannot load it through python's json loads.
        This is not a proper JSON that we can load.

        Instead we manually read values.
        """
        from .url import Url

        url_link = self.get_json_url()
        if url_link:
            url = Url(url_link)
            contents = url.get_contents()

            if contents:
                return contents
            else:
                WebLogger.error("Reddit:No url link contents {}".format(url_link))
        else:
            WebLogger.error("Reddit:no Url link")

    def get_json_value(self, json_text, var):
        wh_start = json_text.find(var)
        if wh_start == -1:
            return

        wh_semi = json_text.find(":", wh_start)
        if wh_semi == -1:
            return

        wh_colon = json_text.find(",", wh_semi)
        if wh_colon == -1:
            return

        text = json_text[wh_semi + 1 : wh_colon].strip()
        return text

    def get_json_data(self):
        result = {}

        json_text = self.get_json_text()

        if not json_text:
            return result

        upvote_ratio = self.get_json_value(json_text, "upvote_ratio")
        try:
            result["upvote_ratio"] = float(upvote_ratio)
        except ValueError:
            result["upvote_ratio"] = None

        return result


class GitHubUrlHandler(DefaultUrlHandler):

    def __init__(self, url=None, contents=None):
        super().__init__(
            url,
            contents=contents,
        )

    def is_handled_by(self):
        if not self.url:
            return False

        code = self.input2code(self.url)
        if code:
            return True

    def input2code(self, input_string):
        p = UrlLocation(input_string)
        if p.get_domain_only().find("github.com") >= 0:
            parts = p.split()
            if len(parts) >= 5:
                return [parts[3], parts[4]]

    def get_json_url(self):
        elements = self.input2code(self.url)
        if elements:
            element_0 = elements[0]
            element_1 = elements[1]
            return f"https://api.github.com/repos/{element_0}/{element_1}"
        else:
            WebLogger.error("GitHub:did not found code {}".format(self.url))

    def get_json_object(self):
        """
        This function loads reddit comment JSON.
        We cannot load it through python's json loads.
        This is not a proper JSON that we can load.

        Instead we manually read values.
        """
        from .url import Url

        url_link = self.get_json_url()
        if url_link:
            url = Url(url_link)
            contents = url.get_contents()

            if contents:
                try:
                    return json.loads(contents)
                except ValueError:
                    WebLogger.error(
                        "GitHub:Cannot process contents {}".format(url_link)
                    )
            else:
                WebLogger.error("GitHub:No url link contents {}".format(url_link))
        else:
            WebLogger.error("GitHub:no Url link")

    def get_json_data(self):
        result = {}

        json = self.get_json_object()

        if json:
            result["thumbs_up"] = json["stargazers_count"]

        return result


class ReturnDislike(DefaultUrlHandler):
    def __init__(self, video_code=None):
        self.code = video_code
        self.process()

    def process(self):
        data = self.read_data()
        self.loads(data)

    def read_data(self):
        from .url import Url

        url = "https://returnyoutubedislikeapi.com/votes?videoId=" + self.code

        u = Url(url)
        data = u.get_contents()
        return data

    def loads(self, data):
        try:
            self._json = json.loads(data)
            return self._json
        except ValueError as E:
            self._json = {}

    def get_json(self):
        return self._json

    def get_thumbs_up(self):
        if self._json and "likes" in self._json:
            return self._json["likes"]

    def get_thumbs_down(self):
        if self._json and "dislikes" in self._json:
            return self._json["dislikes"]

    def get_view_count(self):
        if self._json and "viewCount" in self._json:
            return self._json["viewCount"]

    def get_rating(self):
        if self._json and "rating" in self._json:
            return self._json["rating"]


class HackerNewsHandler(DefaultUrlHandler):

    def __init__(self, url=None, contents=None):
        super().__init__(
            url,
            contents=contents,
        )

    def is_handled_by(self):
        if not self.url:
            return False

        code = self.input2code(self.url)
        if code:
            return True

    def input2code(self, input_string):
        p = UrlLocation(input_string)
        if p.get_domain_only().find("news.ycombinator.com") >= 0:
            parts = p.split()
            if len(parts) >= 5:
                sp = parts[4].split("=")
                if len(sp) > 1:
                    return sp[1]

    def get_json_url(self):
        post_id = self.input2code(self.url)
        if post_id:
            return f"https://hacker-news.firebaseio.com/v0/item/{post_id}.json?print=pretty"
        else:
            WebLogger.error("Reddit:did not found post id {}".format(self.url))

    def get_json_object(self):
        """
        This function loads reddit comment JSON.
        We cannot load it through python's json loads.
        This is not a proper JSON that we can load.

        Instead we manually read values.
        """
        from .url import Url

        url_link = self.get_json_url()
        if url_link:
            url = Url(url_link)
            contents = url.get_contents()

            if contents:
                try:
                    return json.loads(contents)
                except ValueError:
                    WebLogger.error(
                        "GitHub:Cannot process contents {}".format(url_link)
                    )
            else:
                WebLogger.error("GitHub:No url link contents {}".format(url_link))
        else:
            WebLogger.error("GitHub:no Url link")

    def get_json_data(self):
        result = {}

        json = self.get_json_object()

        if json:
            result["upvote_ratio"] = json["score"]

        return result


class InternetArchive(DefaultUrlHandler):
    def __init__(self, url):
        super().__init__(url)

    def get_archive_url(self, time=None):
        if not time:
            return "https://web.archive.org/web/*/" + self.url

        if time:
            time_str = time.strftime("%Y%m%d")
            return "https://web.archive.org/web/{}110000*/".format(time_str) + self.url
