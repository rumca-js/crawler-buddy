import json

from webtoolkit import UrlLocation, RssPage, WebLogger

from .handlerhttppage import HttpPageHandler
from .defaulturlhandler import DefaultUrlHandler, DefaultChannelHandler


class RedditUrlHandler(DefaultUrlHandler):
    """
    Url:
    https://www.reddit.com/r/redditdev/comments/1hw8p3j/i_used_the_reddit_api_to_save_myself_time_with_my/
    Url to JSON:
    https://www.reddit.com/r/redditdev/comments/1hw8p3j/i_used_the_reddit_api_to_save_myself_time_with_my/.json

    Maybe we could use python redditapi
    """

    def __init__(self, url=None, contents=None, settings=None, url_builder=None):
        self.post_id = None
        self.subreddit = None
        self.social_data = {}

        super().__init__(
            url, contents=contents, settings=settings, url_builder=url_builder
        )

    def is_handled_by(self):
        if not self.url:
            return False

        return self.input2code(self.url)

    def input2code(self, input_string):
        p = UrlLocation(input_string)
        if p.get_domain_only().find("reddit.com") >= 0:
            parts = p.split()
            if len(parts) >= 6 and parts[3] == "r" and parts[5] == "comments":
                self.subreddit = parts[4]
                self.post_id = parts[6]

                return True
            if len(parts) >= 4 and parts[3] == "r":
                self.subreddit = parts[4]
                return True

    def get_json_url(self):
        self.input2code(self.url)
        if self.post_id:
            return f"https://www.reddit.com/{self.post_id}.json"
        elif self.subreddit:
            return f"https://www.reddit.com/r/{self.subreddit}/.json"
        else:
            WebLogger.error("Reddit:did not found post id {}".format(self.url))

    def get_json_text(self):
        """
        This function loads reddit comment JSON.
        We cannot load it through python's json loads.
        This is not a proper JSON that we can load.

        Instead we manually read values.
        """
        url_link = self.get_json_url()
        if url_link:

            settings = {}
            settings["handler_class"] = HttpPageHandler
            url = self.url_builder(url=url_link, settings=settings)
            contents = url.get_contents()

            if contents:
                return contents
            else:
                WebLogger.error("Reddit:No url link contents {}".format(url_link))
        else:
            WebLogger.error("Reddit:no Url link")

    def get_json_value(self, json_text, var):
        wh_start = json_text.find('"{}"'.format(var))
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
        if self.social_data != {}:
            return self.social_data

        json_text = self.get_json_text()

        if not json_text:
            return self.social_data

        if self.post_id:
            upvote_ratio = self.get_json_value(json_text, "upvote_ratio")
            try:
                upvote_ratio = float(upvote_ratio)
            except ValueError:
                upvote_ratio = None

            score = self.get_json_value(json_text, "score")
            try:
                score = float(score)
            except ValueError:
                score = None

            self.social_data["upvote_ratio"] = upvote_ratio
            self.social_data["rating"] = score
        elif self.subreddit:
            subscribers = self.get_json_value(json_text, "subreddit_subscribers")
            try:
                subscribers = int(subscribers)
            except ValueError:
                subscribers = None

            self.social_data["followers_count"] = subscribers

        return self.social_data

    def get_upvote_ratio(self):
        if self.social_data:
            return self.social_data.get("upvote_ratio")

    def get_followers_count(self):
        if self.social_data:
            return self.social_data.get("followers_count")

    def get_social_data(self):
        """
        If we did not receive social data, do not return anything
        """
        if len(self.social_data) > 0:
            return super().get_social_data()

    def get_feeds(self):
        """
        even for post, or individual videos we might request feed url
        """
        feeds = super().get_feeds()

        if self.subreddit:
            feeds.append("https://www.reddit.com/r/{}/.rss".format(self.subreddit))

        return feeds


class GitHubUrlHandler(DefaultUrlHandler):

    def __init__(self, url=None, contents=None, settings=None, url_builder=None):
        self.social_data = {}

        super().__init__(
            url, contents=contents, settings=settings, url_builder=url_builder
        )

    def is_handled_by(self):
        if not self.url:
            return False

        code = self.input2code(self.url)
        if code:
            return True

    def input2code(self, input_string):
        p = UrlLocation(input_string)
        domain_only = p.get_domain_only()

        if domain_only.find("api.github.com") >= 0:
            parts = p.split()
            if len(parts) >= 6:
                return [parts[4], parts[5]]
        elif domain_only.find("github.com") >= 0:
            parts = p.split()
            if len(parts) >= 5:
                return [parts[3], parts[4]]

    def get_feeds(self):
        """
        even for post, or individual videos we might request feed url
        """
        feeds = super().get_feeds()

        elements = self.input2code(self.url)
        if elements:
            owner = elements[0]
            repository = elements[1]
            feeds.append(
                "https://github.com/{}/{}/commits.atom".format(owner, repository)
            )
            feeds.append(
                "https://github.com/{}/{}/releases.atom".format(owner, repository)
            )

        return feeds

    def get_json_url(self):
        elements = self.input2code(self.url)
        if elements:
            owner = elements[0]
            repository = elements[1]
            return f"https://api.github.com/repos/{owner}/{repository}"
        else:
            WebLogger.error("GitHub:did not found code {}".format(self.url))

    def get_json_object(self):
        """
        This function loads reddit comment JSON.
        We cannot load it through python's json loads.
        This is not a proper JSON that we can load.

        Instead we manually read values.
        """

        url_link = self.get_json_url()
        if url_link:
            settings = {}
            settings["handler_class"] = HttpPageHandler
            url = self.url_builder(url=url_link, settings=settings)
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
        if self.social_data != {}:
            return self.social_data

        self.social_data = {}

        json = self.get_json_object()

        if json:
            self.social_data["stars"] = json["stargazers_count"]

        return self.social_data

    def get_user_stars(self):
        return self.social_data.get("stars")


class ReturnDislike(DefaultUrlHandler):
    def __init__(
        self, video_code=None, url=None, contents=None, settings=None, url_builder=None
    ):

        if video_code:
            url = self.code2url(video_code)

        super().__init__(
            url=url, contents=contents, settings=settings, url_builder=url_builder
        )

    def code2url(self, input_code):
        return "https://returnyoutubedislikeapi.com/votes?videoId=" + input_code

    def is_handled_by(self):
        return False

    def load_response(self):
        self.get_response()
        contents = self.get_contents()
        self._json = self.loads(contents)
        return self._json

    def loads(self, data):
        try:
            self._json = json.loads(data)
            return self._json
        except ValueError as E:
            self._json = {}

    def get_json(self):
        return self._json

    def get_thumbs_up(self):
        if self._json:
            return self._json.get("likes")

    def get_thumbs_down(self):
        if self._json:
            return self._json.get("dislikes")

    def get_view_count(self):
        if self._json:
            return self._json.get("viewCount")

    def get_rating(self):
        if self._json:
            return self._json.get("rating")

    def get_json_data(self):
        self.get_response()


class HackerNewsHandler(DefaultUrlHandler):

    def __init__(self, url=None, contents=None, settings=None, url_builder=None):
        self.social_data = {}
        super().__init__(
            url, contents=contents, settings=settings, url_builder=url_builder
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

        url_link = self.get_json_url()
        if url_link:
            settings = {}
            settings["handler_class"] = HttpPageHandler
            url = self.url_builder(url=url_link, settings=settings)
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
        if self.social_data != {}:
            return self.social_data

        self.social_data = {}

        json = self.get_json_object()

        if json:
            self.social_data["upvote_diff"] = json["score"]

        return self.social_data

    def get_upvote_diff(self):
        if "upvote_diff" in self.social_data:
            return self.social_data["upvote_diff"]


class InternetArchive(DefaultUrlHandler):
    def __init__(self, url, settings=None, url_builder=None):
        super().__init__(url, settings=settings, url_builder=url_builder)

    def is_handled_by(self):
        p = UrlLocation(self.url)
        if p.get_domain_only().find("archive.org") >= 0:
            return True

    def get_archive_url(self, time=None):
        if not time:
            return "https://web.archive.org/web/*/" + self.url

        if time:
            time_str = time.strftime("%Y%m%d")
            return "https://web.archive.org/web/{}110000*/".format(time_str) + self.url


class FourChanChannelHandler(DefaultChannelHandler):
    def __init__(self, url=None, contents=None, settings=None, url_builder=None):
        super().__init__(
            url, contents=contents, settings=settings, url_builder=url_builder
        )

        if url:
            self.code = self.input2code(url)

    def is_handled_by(self):
        if not self.url:
            return False

        p = UrlLocation(self.url)
        if p.get_domain_only().find("4chan.org") >= 0:
            return True

    def input2code(self, input_string):
        p = UrlLocation(input_string)
        domain_only = p.get_domain_only()

        if domain_only.find("boards.4chan.org") >= 0:
            parts = p.split()
            if len(parts) >= 3:
                return parts[3]
        elif domain_only.find("4chan.org") >= 0:
            parts = p.split()
            if len(parts) >= 3:
                return parts[3]

    def get_feeds(self):
        """
        even for post, or individual videos we might request feed url
        """
        feeds = super().get_feeds()

        if self.code:
            feeds.append("https://boards.4chan.org/{}/index.rss".format(self.code))

        return feeds


class TwitterUrlHandler(DefaultUrlHandler):

    def __init__(self, url=None, contents=None, settings=None, url_builder=None):
        super().__init__(
            url, contents=contents, settings=settings, url_builder=url_builder
        )
        wh = self.url.find("?ref_src=")
        if wh >= 0:
            self.url = self.url[:wh]

    def is_handled_by(self):
        if not self.url:
            return False

        if self.url.find("https://x.com") >= 0:
            return True
        if self.url.find("https://twitter.com") >= 0:
            return True
