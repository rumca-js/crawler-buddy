import urllib.parse

from rsshistory.webtools import UrlLocation


class Validator(object):
    def __init__(self, url):
        self.url = url

    def validate(self):
        pass

    def get_validate_url(self):
        pass

    def encode_url(self, url):
        return urllib.parse.quote(url)


class WhoIs(Validator):
    def __init__(self, url):
        self.url = url

    def get_validate_url(self):
        p = UrlLocation(self.url)
        return "https://who.is/whois/" + p.get_domain_only()


class W3CValidator(Validator):
    def __init__(self, url):
        self.url = url

    def get_validate_url(self):
        return "https://validator.w3.org/nu/?doc=" + self.encode_url(self.url)


class SchemaOrg(Validator):
    def __init__(self, url):
        self.url = url

    def get_validate_url(self):
        return "https://validator.schema.org/#url=" + self.encode_url(self.url)
