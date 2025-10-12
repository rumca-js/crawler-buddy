from webtoolkit import DefaultContentPage, calculate_hash_binary, calculate_hash


class HandlerInterface(DefaultContentPage):
    """
    Default URL handler.
    Behavior can be changed by setting .h handler property

    There can be various means of accessing things on the internet. we may use browsers, or programs
    this allows us to provide interface
    """

    def __init__(self, url=None, contents=None, settings=None, url_builder=None):
        super().__init__(
            url,
            contents=contents,
        )
        self.h = None
        self.response = None
        self.streams = {}
        self.dead = None
        self.code = None  # social media handle, ID of channel, etc.
        self.settings = settings
        self.handler = None  # for example rss UrlHandler
        self.url_builder = url_builder

    def is_handled_by(self):
        return True

    def get_url(self):
        if self.code:
            return self.code2url(self.code)
        else:
            return self.url

    def get_canonical_url(self):
        return self.get_url()

    def get_feeds(self):
        """
        even for post, or individual videos we might request feed url
        """
        return []

    def input2code(self, input_string):
        pass

    def input2url(self, input_string):
        raise NotImplementedError

    def get_code(self):
        raise NotImplementedError

    def code2url(self, input_code):
        pass

    def code2feed(self, code):
        pass

    def get_name(self):
        raise NotImplementedError

    def get_contents(self):
        if self.response:
            return self.response.get_text()

    def get_contents_hash(self):
        if self.response is None:
            self.get_response()

        if self.response is not None:
            text = self.response.get_text()
            if text:
                return calculate_hash(text)

            binary = self.response.get_binary()
            if binary:
                return calculate_hash_binary(binary)

    def get_streams(self):
        if "Text" not in self.streams:
            if self.response is not None:
                self.streams["Text"] = self.response.get_text()

                if self.streams["Text"] is None:
                    self.streams["Binary"] = self.response.get_binary()
        return self.streams

    def get_contents_body_hash(self):
        return self.get_contents_hash()

    def get_title(self):
        if self.handler:
            return self.handler.get_title()

    def get_description(self):
        if self.handler:
            return self.handler.get_description()

    def get_language(self):
        if self.handler:
            return self.handler.get_language()

    def get_thumbnail(self):
        if self.handler:
            return self.handler.get_thumbnail()

    def get_author(self):
        if self.handler:
            return self.handler.get_author()

    def get_album(self):
        if self.handler:
            return self.handler.get_album()

    def get_tags(self):
        if self.handler:
            return self.handler.get_tags()

    def get_date_published(self):
        if self.handler:
            return self.handler.get_date_published()

    def get_status_code(self):
        if self.response:
            return self.response.get_status_code()

        return 0

    def get_entries(self):
        return []

    def get_response(self):
        raise NotImplementedError

    def ping(self, timeout_s=120):
        """
        @param timeout_s 0 is unlimited
        """
        raise NotImplementedError

    def get_view_count(self):
        """ """
        return

    def get_rating(self):
        return

    def get_thumbs_up(self):
        return

    def get_thumbs_down(self):
        return

    def get_upvote_ratio(self):
        thumbs_up = self.get_thumbs_up()
        thumbs_down = self.get_thumbs_down()

        if thumbs_up is not None and thumbs_down is not None:
            all = thumbs_down + thumbs_up

            return thumbs_up / all

    def get_upvote_diff(self):
        thumbs_up = self.get_thumbs_up()
        thumbs_down = self.get_thumbs_down()
        if thumbs_up is not None and thumbs_down is not None:
            return thumbs_up - thumbs_down

    def get_upvote_view_ratio(self):
        thumbs_up = self.get_thumbs_up()
        views = self.get_view_count()

        if thumbs_up is not None and views is not None and views > 0:
            return thumbs_up / views

    def get_user_stars(self):
        """
        stars / favourites
        """
        pass

    def get_followers_count(self):
        """
        followers / subscribers
        """
        pass

    def get_json_data(self):
        """
        Called to obtain link json data (dynamic data)
        """
        pass

    def get_social_data(self):
        """
        This function returns:
         - social data, if it has them
         - nothing in case of error
        """
        json_obj = {}

        json_obj["thumbs_up"] = self.get_thumbs_up()
        json_obj["thumbs_down"] = self.get_thumbs_down()
        json_obj["view_count"] = self.get_view_count()
        json_obj["rating"] = self.get_rating()
        json_obj["upvote_ratio"] = self.get_upvote_ratio()
        json_obj["upvote_diff"] = self.get_upvote_diff()
        json_obj["upvote_view_ratio"] = self.get_upvote_view_ratio()
        json_obj["stars"] = self.get_user_stars()
        json_obj["followers_count"] = self.get_followers_count()

        return json_obj
