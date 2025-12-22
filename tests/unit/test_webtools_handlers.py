from webtoolkit import (
   RedditUrlHandler,
   GitHubUrlHandler,
   HackerNewsHandler,
   TwitterUrlHandler,
   FourChanChannelHandler,
)

from src.webtools import (
   Url,
)
from tests.unit.fakeinternet import (
   FakeInternetTestCase, MockRequestCounter
)


class RedditUrlHandlerTest(FakeInternetTestCase):
    def setUp(self):
        self.disable_web_pages()

    def test_constructor(self):
        test_link = "https://www.reddit.com/r/redditdev/comments/1hw8p3j/i_used_the_reddit_api_to_save_myself_time_with_my/"

        handler = RedditUrlHandler(test_link, url_builder=Url)

        data = handler.get_json_data()

        self.assertIn("upvote_ratio", data)
        #self.assertIn("thumbs_up", data)
        #self.assertIn("thumbs_down", data)

    def test_input2code(self):
        test_link = "https://www.reddit.com/r/CursedAI"

        handler = RedditUrlHandler(test_link, url_builder=Url)

        # call tested function
        self.assertEqual("CursedAI", handler.subreddit)

    def test_get_feeds__channel(self):
        test_link = "https://www.reddit.com/r/CursedAI"

        handler = RedditUrlHandler(test_link, url_builder=Url)

        # call tested function
        feeds = handler.get_feeds()

        self.assertIn("https://www.reddit.com/r/CursedAI/.rss", feeds)

    def test_get_feeds__comments(self):
        test_link = "https://www.reddit.com/r/redditdev/comments/1hw8p3j/i_used_the_reddit_api_to_save_myself_time_with_my"

        handler = RedditUrlHandler(test_link, url_builder=Url)

        # call tested function
        feeds = handler.get_feeds()

        self.assertIn("https://www.reddit.com/r/redditdev/.rss", feeds)

    def test_get_json_data__comment(self):
        MockRequestCounter.mock_page_requests = 0

        test_link = "https://www.reddit.com/r/redditdev/comments/1hw8p3j/i_used_the_reddit_api_to_save_myself_time_with_my/"

        url = RedditUrlHandler(test_link, url_builder=Url)

        # call tested function
        properties = url.get_json_data()

        self.assertIn("upvote_ratio", properties)
        self.assertTrue(properties["upvote_ratio"])

        self.assertEqual(MockRequestCounter.mock_page_requests, 1)

    def test_get_json_data__subreddit(self):
        MockRequestCounter.mock_page_requests = 0

        test_link = "https://www.reddit.com/r/InternetIsBeautiful"

        url = RedditUrlHandler(test_link, url_builder=Url)

        # call tested function
        properties = url.get_json_data()

        self.assertIn("followers_count", properties)
        self.assertTrue(properties["followers_count"])

        self.assertEqual(MockRequestCounter.mock_page_requests, 1)


class GitHubUrlHandlerTest(FakeInternetTestCase):
    def setUp(self):
        self.disable_web_pages()

    def test_is_handled_by__repository(self):
        test_link = "https://github.com/rumca-js/Django-link-archive/commits.atom"

        handler = GitHubUrlHandler(test_link, url_builder=Url)

        # call tested function
        self.assertTrue(handler.is_handled_by())

    def test_is_handled_by__api(self):
        test_link = "https://api.github.com/repos/rumca-js/Django-link-archive"

        handler = GitHubUrlHandler(test_link, url_builder=Url)

        # call tested function
        self.assertTrue(handler.is_handled_by())

    def test_input2code__repository(self):
        test_link = "https://github.com/rumca-js/Django-link-archive/commits.atom"

        handler = GitHubUrlHandler(test_link, url_builder=Url)

        # call tested function
        self.assertIn("Django-link-archive", handler.input2code(test_link))
        self.assertIn("rumca-js", handler.input2code(test_link))

    def test_input2code__api(self):
        test_link = "https://api.github.com/repos/rumca-js/Django-link-archive"

        handler = GitHubUrlHandler(test_link, url_builder=Url)

        # call tested function
        self.assertIn("Django-link-archive", handler.input2code(test_link))
        self.assertIn("rumca-js", handler.input2code(test_link))

    def test_get_feeds(self):
        test_link = "https://api.github.com/repos/rumca-js/Django-link-archive"

        handler = GitHubUrlHandler(test_link, url_builder=Url)

        # call tested function
        feeds = handler.get_feeds()

        self.assertIn("https://github.com/rumca-js/Django-link-archive/commits.atom", feeds)

    def test_get_json_url(self):
        test_link = "https://api.github.com/repos/rumca-js/Django-link-archive"

        handler = GitHubUrlHandler(test_link, url_builder=Url)

        # call tested function
        url = handler.get_json_url()

        self.assertEqual("https://api.github.com/repos/rumca-js/Django-link-archive", url)

    def test_get_json_data(self):
        test_link = "https://api.github.com/repos/rumca-js/Django-link-archive"

        handler = GitHubUrlHandler(test_link, url_builder=Url)

        # call tested function
        data = handler.get_json_data()

        self.assertIn("stars", data)


class HackerNewsHandlerTest(FakeInternetTestCase):
    def setUp(self):
        self.disable_web_pages()

    def test_constructor(self):
        test_link = "https://news.ycombinator.com/item?id=42728015"

        handler = HackerNewsHandler(test_link, url_builder=Url)

        data = handler.get_json_data()
        self.assertEqual(handler.get_json_url(), "https://hacker-news.firebaseio.com/v0/item/42728015.json?print=pretty")

        self.assertIn("upvote_diff", data)


class TwitterUrlHandlerTest(FakeInternetTestCase):
    def setUp(self):
        self.disable_web_pages()

    def test_is_handled_by(self):
        test_link = "https://x.com/RockstarGames?ref_src=twsrc%5Egoogle%7Ctwcamp%5Eserp%7Ctwgr%5Eauthor"

        handler = TwitterUrlHandler(test_link, url_builder=Url)

        # call tested function
        self.assertTrue(handler.is_handled_by())

    def test_url(self):
        test_link = "https://x.com/RockstarGames?ref_src=twsrc%5Egoogle%7Ctwcamp%5Eserp%7Ctwgr%5Eauthor"

        handler = TwitterUrlHandler(test_link)

        expected_link = "https://x.com/RockstarGames"

        # call tested function
        self.assertEqual(handler.url, expected_link)


class FourChanChannelHandlerTest(FakeInternetTestCase):
    def setUp(self):
        self.disable_web_pages()

    def test_input2code(self):
        test_link = "https://4chan.org/test/"

        handler = FourChanChannelHandler(test_link, url_builder=Url)

        # call tested function
        self.assertEqual("test", handler.code)

    def test_get_feeds(self):
        test_link = "https://4chan.org/test/"

        handler = FourChanChannelHandler(test_link, url_builder=Url)

        # call tested function
        # self.assertEqual(["https://boards.4chan.org/test/index.rss"], handler.get_feeds())
