from .pages import DefaultContentPage


class HandlerInterface(DefaultContentPage):
    """
    Default URL handler.
    Behavior can be changed by setting .h handler property

    There can be various means of accessing things on the internet. we may use browsers, or programs
    this allows us to provide interface
    """

    def __init__(self, url=None, contents=None, page_options=None, url_builder=None):
        super().__init__(
            url,
            contents=contents,
        )
        self.h = None
        self.response = None
        self.dead = None
        self.code = None  # social media handle, ID of channel, etc.
        self.options = page_options
        self.handler = None  # for example rss UrlHandler
        self.url_builder = url_builder

    def is_handled_by(self):
        return True

    def get_url(self):
        if self.code:
            return self.code2url(self.code)
        else:
            return self.url

    def get_feeds(self):
        """
        even for post, or individual videos we might request feed url
        """
        if self.code:
            return [self.code2feed(self.code)]
        return []

    def input2code(self, input_string):
        raise NotImplementedError

    def input2url(self, input_string):
        raise NotImplementedError

    def get_code(self):
        raise NotImplementedError

    def code2url(self, input_code):
        raise NotImplementedError

    def code2feed(self, code):
        raise NotImplementedError

    def get_name(self):
        raise NotImplementedError

    def get_contents(self):
        if self.response:
            return self.response.get_text()

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

    def ping(self, timeout_s = 120):
        """
        @param timeout_s 0 is unlimited
        """
        raise NotImplementedError
