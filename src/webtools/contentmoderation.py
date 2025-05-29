from .webtools import WebLogger


class UrlContentsModerator(object):
    def __init__(self, page_object=None, properties=None, blocked_keywords=None):
        self.properties = []

    def get_title(self):
        if "title" in self.properties:
            if self.properties["title"] is None:
                return ""
            return self.properties["title"]
        else:
            return ""

    def get_description(self):
        if "description" in self.properties:
            if self.properties["description"] is None:
                return ""
            return self.properties["description"]
        else:
            return ""

    def get_descriptive_pulp(self):
        title = self.get_title()
        title = title.lower()

        description = self.get_description()
        description = description.lower()

        return title + "\n" + description


class UrlPropertyValidator(UrlContentsModerator):
    def __init__(self, page_object=None, properties=None, blocked_keywords=None):
        self.properties = []
        if page_object:
            self.properties = page_object.get_properties()
        if properties:
            self.properties = properties

        if blocked_keywords and len(blocked_keywords) > 0:
            self.blocked_keywords = blocked_keywords
        else:
            self.blocked_keywords = [
                "masturbat",
                "porn",
                "xxx",
                "sex",
                "slutt",
                "nude",
                "chaturbat",
            ]

    def is_valid(self):
        if self.is_site_not_found():
            return False

        if self.is_porn_blocked():
            return False

        if self.is_casino_blocked():
            return False

        if self.is_blocked_keywords():
            return False

        return True

    def is_blocked_keywords(self):
        """
        TODO This should be configurable - move to configuration
        """
        title = self.get_title()
        title = title.lower()

        for keyword in self.blocked_keywords:
            if title.find(keyword) >= 0:
                return True

        return False

    def is_site_not_found(self):
        title = self.get_title()
        if title:
            title = title.lower()
        else:
            title = ""

        is_title_invalid = (
            title.find("forbidden") >= 0
            or title.find("access denied") >= 0
            or title.find("site not found") >= 0
            or title.find("page not found") >= 0
            or title.find("this page could not found") >= 0
            or title.find("404 not found") >= 0
            or title.find("404: not found") >= 0
            or title.find("404 not_found") >= 0
            or title.find("404 - not found") >= 0
            or title.find("404 error") >= 0
            or title.find("404 page") >= 0
            or title.find("404 file not found") >= 0
            or title.find("error 404") >= 0
            or title.find("purged account") >= 0
            or title.find("410 gone") >= 0
            or title.find("squarespace - website expired") >= 0
            or title.find("domain name for sale") >= 0
            or title.find("account suspended") >= 0
            or title.find("the request could not be satisfied") >= 0
        )

        if is_title_invalid:
            WebLogger.debug("Title is invalid {}".format(title))
            return True

    def is_porn_blocked(self):
        """
        TODO This should be configurable - move to configuration
        """
        title = self.get_title()
        title = title.lower()

        porn_keywords = [
            "masturbat",
            "porn",
            "xxx",
            "sex",
            "slutt",
            "nude",
            "chaturbat",
        ]

        for keyword in porn_keywords:
            if title.find(keyword) >= 0:
                return True

        keywords = [
            "live",
            "nast",
            "slut",
            "webcam",
        ]

        points = 0
        for keyword in keywords:
            if title.find(keyword) >= 0:
                points += 1

        return points > 3

    def is_casino_blocked(self):
        """
        TODO This should be configurable - move to configuration
        """
        title = self.get_title()
        title = title.lower()

        if title.find("slot server") >= 0:
            return True

        description = self.get_description()
        description = description.lower()

        text = title + "\n" + description

        keywords = [
            "casino",
            "lotter",
            "bingo",
            "slot",
            "poker",
            "jackpot",
            "gacor",
            "bandar judi",
            "pagcor",
            "slotlara kadar",
            "canli bahis",
            "terpopuler",
            "deposit",
        ]

        sum = 0
        for keyword in keywords:
            sum += text.count(keyword)

        return sum > 3


class UrlAgeModerator(UrlContentsModerator):
    def __init__(self, page_object=None, properties=None, blocked_keywords=None):
        self.properties = []
        if page_object:
            self.properties = page_object.get_properties()
        if properties:
            self.properties = properties

    def get_age(self):
        """
        implement more types of checks?

        @return age requirement, or None
        """
        age0 = self.get_age__sexual()

        return age0

    def get_age__sexual(self):
        text = self.get_descriptive_pulp()

        keywords = [
            "sexua",
            "lesbian",
            "bisexual",
            "queer ",
            "drag quee",
            "fuck",
            "porn",
            "nsfw",
        ]

        sum = 0
        for keyword in keywords:
            sum += text.count(keyword)

        if sum > 1:
            return 15
