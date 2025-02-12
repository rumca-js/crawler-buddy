from utils.sqlmodel import (
    SqlModel,
    EntriesTable,
)


class GenericEntryController(object):
    def __init__(self, entry, console=False):
        self.entry = entry
        self.console_printer = console

    def get_title(self, full_title=False):
        if not self.entry.title:
            return

        if not full_title:
            title = self.entry.title[:100]
        else:
            title = self.entry.title

        bracket_text = self.get_bracket_text()
        code = self.get_title_info_string()

        if code:
            title = "[{}] {}".format(code, title)

        if bracket_text:
            title = "[{}] {}".format(bracket_text, title)

        return title

    def get_bracket_text(self):
        id = self.entry.id
        votes = self.entry.page_rating_votes
        contents = self.entry.page_rating_contents

        text = ""

        if self.console_printer:
            text += str(id)

        if votes > 0:
            if text != "":
                text += "|"
            text += "{}".format(votes)

        # if contents:
        #    if text != "":
        #        text += "|"
        #    text += "{} ".format(contents)

        return text

    def get_title_info_string(self):
        code = ""
        if self.is_dead():
            code += "D"
        if self.entry.age != 0 and self.entry.age is not None:
            code += "A"
        if self.entry.page_rating_votes < 0:
            code += "V"

        if self.console_printer:
            if self.entry.bookmarked:
                code += "B"

        return code

    def is_dead(self):
        """
        We do not have to make elaborate checks for statuses and manual statuses.
        If there is a dead date -> it is dead. Period.
        """
        return self.entry.date_dead_since is not None


class EntryDataBuilder(object):
    """ """

    def __init__(
        self,
        conn,
        link=None,
        link_data=None,
        source_is_auto=True,
        allow_recursion=True,
        ignore_errors=False,
    ):
        self.link = link
        self.link_data = link_data
        self.source_is_auto = source_is_auto
        self.allow_recursion = allow_recursion

        self.ignore_errors = ignore_errors
        c = Configuration.get_object().config_entry
        if c.accept_dead:
            self.ignore_errors = True

        self.result = None

        if self.link:
            self.build_from_link()

        if self.link_data:
            self.build_from_props(ignore_errors=self.ignore_errors)

    def build(
        self,
        link=None,
        link_data=None,
        source_is_auto=True,
        allow_recursion=True,
        ignore_errors=False,
    ):
        self.link = link
        self.link_data = link_data

        if self.link:
            self.build_from_link()

        if self.link_data:
            self.build_from_props(ignore_errors=self.ignore_errors)

    def build_from_link(self, ignore_errors=False):
        """
        TODO extract this to a separate class?
        """
        from src.webtools import Url, UrlPropertyValidator

        self.ignore_errors = ignore_errors
        self.link = Url.get_cleaned_link(self.link)
        if not self.link:
            return

        url = Url(self.link)
        self.link_data = url.get_properties()
        self.build_from_props()

    def build_from_props(self, ignore_errors=False):
        from src.webtools import Url, UrlPropertyValidator

        self.ignore_errors = ignore_errors

        url = self.link_data["link"]
        if not url:
            return

        obj = None

        self.link_data["link"] = Url.get_cleaned_link(self.link_data["link"])
        self.link = self.link_data["link"]

        Session = self.get_session()
        with Session() as session:
            table = EntriesTable(**self.link_data)
            session.add(table)
            session.commit()
