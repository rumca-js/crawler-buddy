from urllib.parse import urlparse, parse_qs
from .webtools import (
    URL_TYPE_RSS,
    URL_TYPE_CSS,
    URL_TYPE_JAVASCRIPT,
    URL_TYPE_HTML,
    URL_TYPE_FONT,
    URL_TYPE_UNKNOWN,
)


class UrlLocation(object):
    def __init__(self, url):
        self.url = url

    def is_web_link(self):
        """
        Hosts may redefine addresses, but these are NOT real web links
        """
        if (
            self.url.startswith("http://")
            or self.url.startswith("https://")
            or self.url.startswith("smb://")
            or self.url.startswith("ftp://")
            or self.url.startswith("//")
            or self.url.startswith("\\\\")
        ):
            # https://mailto is not a good link
            if self.url.find(".") == -1:
                return False

            # no funny chars
            domain_only = self.get_domain_only()
            if not domain_only:
                return False
            if domain_only.find("&") >= 0:
                return False
            if domain_only.find("?") >= 0:
                return False

            parts = domain_only.split(".")
            if parts[0].strip() == "":
                return False

            return True

        return False

    def is_protocolled_link(self):
        if (
            self.url.startswith("http://")
            or self.url.startswith("https://")
            or self.url.startswith("smb://")
            or self.url.startswith("ftp://")
            or self.url.startswith("email://")
            or self.url.startswith("//")
            or self.url.startswith("\\\\")
        ):
            return True
        return False

    def get_protocolless(self):
        protocol_pos = self.url.find("://")
        if protocol_pos >= 0:
            return self.url[protocol_pos + 3 :]

        return self.url

    def get_full_url(self):
        if self.url.lower().find("http") == -1:
            return "https://" + self.url
        return self.url

    def get_port(self):
        parts = self.parse_url()

        if not parts:
            return

        if len(parts) > 1:
            wh = parts[2].find(":")
            if wh == -1:
                return
            else:
                try:
                    port = int(parts[2][wh + 1 :])
                    return port
                except ValueError as E:
                    return

    def get_protocol_url(self, protocol="https"):
        """
        replaces any protocol with input protocol
        """
        protocol_pos = self.url.find("://")
        if protocol_pos >= 0:
            return protocol + "://" + self.url[protocol_pos + 3 :]

        return self.url

    def parse_url(self):
        """
        We cannot use urlparse, as it does not work with ftp:// or smb:// or win location
        returns tuple [protocol, separator, url]
        """
        if not self.url:
            return

        protocol_pos = self.url.find("://")
        if protocol_pos >= 0:
            return self.parse_protocoled_url()

        elif self.url.startswith("//"):
            return self.parse_netloc("//")
        elif self.url.startswith("\\\\"):
            return self.parse_netloc("\\\\")

        else:
            return ["https", "://", self.url]

    def parse_protocoled_url(self):
        protocol_pos = self.url.find("://")
        if protocol_pos >= 0:
            rest = self.url[protocol_pos + 3 :]
            protocol = self.url[:protocol_pos].lower()

            rest_data = self.parse_location(rest)

            if len(rest_data) > 1:
                args = self.parse_argument(rest_data[1])
                if args[1] != "":
                    return [protocol, "://", rest_data[0], args[0], args[1]]
                else:
                    return [protocol, "://", rest_data[0], rest_data[1]]
            else:
                return [protocol, "://", rest_data[0]]

    def parse_netloc(self, separator="//"):
        """
        returns [domain, separator, rest of the link]
        """
        if self.url.startswith(separator):
            if separator == "//":
                lesser_separator = "/"
            else:
                lesser_separator = "\\"

            rest = self.url[len(separator) :]

            rest_data = self.parse_location(rest)

            if len(rest_data) > 1:
                args = self.parse_argument(rest_data[1])
                if args[1] != "":
                    return ["", separator, rest_data[0], args[0], args[1]]
                else:
                    return ["", separator, rest_data[0], rest_data[1]]
            else:
                return ["", separator, rest_data[0]]

    def parse_location(self, rest):
        """
        returns tuple [link, arguments]
        """
        wh1 = rest.find("/")
        wh2 = rest.find("\\")
        wh3 = rest.find("?")
        wh4 = rest.find("#")
        positions = [wh for wh in [wh1, wh2, wh3, wh4] if wh != -1]

        if len(positions) > 0:
            smallest_position = min(positions)
            return [rest[:smallest_position], rest[smallest_position:]]
        return [rest, ""]

    def parse_argument(self, rest):
        """
        returns tuple [link, arguments]
        """
        wh1 = rest.find("?")
        wh2 = rest.find("#")
        positions = [wh for wh in [wh1, wh2] if wh != -1]

        if len(positions) > 0:
            smallest_position = min(positions)
            return [rest[:smallest_position], rest[smallest_position:]]
        return [rest, ""]

    def get_domain(self):
        """
        for https://domain.com/test

        @return https://domain.com
        """
        if not self.url:
            return

        parts = self.parse_url()

        wh = parts[2].find(":")
        if wh >= 0:
            parts[2] = parts[2][:wh]

        text = parts[0] + parts[1] + parts[2].lower()

        x = UrlLocation(text)
        if self.url and not x.is_protocolled_link():
            return

        if text.strip() == "http://" or text.strip() == "https://":
            return

        # if passed email, with user
        wh = text.find("@")
        if wh >= 0:
            return parts[0] + parts[1] + text[wh + 1 :]

        return text

    def get_domain_only(self):
        """
        for https://domain.com/test

        @return domain.com
        """
        parts = self.parse_url()
        if parts:
            return parts[2].lower()

    def get_scheme(self):
        parts = self.parse_url()
        if parts:
            return parts[0]

    def is_domain(self):
        if not self.url:
            return False

        url = self.get_full_url()
        if url == self.get_domain():
            return True

        return False

    def get_page_ext(self):
        """
        @return extension, or none
        """
        url = self.get_clean_url()

        # domain level does not say anything if it is HTML page, or not
        if url == self.get_domain():
            return

        if url.endswith("/"):
            return

        sp = url.split(".")
        if len(sp) > 1:
            ext = sp[-1]
            if len(ext) < 5:
                return ext

        return

    def get_clean_url(self):
        url = self.url
        if url.find("?") >= 0:
            wh = url.find("?")
            return url[:wh]
        else:
            return url

    def get_url_full(domain, url):
        """
        TODO change function name
        formats:
        href="images/facebook.png"
        href="/images/facebook.png"
        href="//images/facebook.png"
        href="https://images/facebook.png"
        """
        ready_url = ""
        if url.lower().find("http") == 0:
            ready_url = url
        else:
            if url.startswith("//"):
                ready_url = "https:" + url
            elif url.startswith("/"):
                domain = UrlLocation(domain).get_domain()
                if not domain.endswith("/"):
                    domain = domain + "/"
                if url.startswith("/"):
                    url = url[1:]

                ready_url = domain + url
            else:
                if not domain.endswith("/"):
                    domain = domain + "/"
                ready_url = domain + url
        return ready_url

    def up(self, skip_internal=False):
        if self.is_domain():
            return self.up_domain()
        else:
            if skip_internal:
                domain = self.get_domain()
                return UrlLocation(domain)
            return self.up_not_domain()

    def up_domain(self):
        """
        https://github.com
        """
        domain = self.url
        if domain.count(".") == 1:
            return None

        else:
            parts = self.parse_url()
            if len(parts) < 3:
                return

            sp = parts[2].split(".")
            url = parts[0] + parts[1] + ".".join(sp[1:])
            return UrlLocation(url)

    def up_not_domain(self):
        url = self.url
        wh = self.url.rfind("/")
        if wh >= 0:
            return UrlLocation(self.url[:wh])

    def is_mainstream(self):
        dom = self.get_domain_only()

        # wallet gardens which we will not accept

        mainstream = [
            "www.facebook",
            "www.rumble",
            "wikipedia.org",
            "twitter.com",
            "www.reddit.com",
            "stackoverflow.com",
            "www.quora.com",
            "www.instagram.com",
        ]

        for item in mainstream:
            if dom.find(item) >= 0:
                return True

        if self.is_youtube():
            return True

        return False

    def is_youtube(self):
        dom = self.get_domain_only()
        if (
            dom == "youtube.com"
            or dom == "youtu.be"
            or dom == "www.m.youtube.com"
            or dom == "m.youtube.com"
            or dom == "www.youtube.com"
        ):
            return True
        return False

    def is_analytics(self):
        url = self.get_domain_only()

        if not url:
            return False

        if url.find("g.doubleclick.net") >= 0:
            return True
        if url.find("ad.doubleclick.net") >= 0:
            return True
        if url.find("doubleverify.com") >= 0:
            return True
        if url.find("adservice.google.com") >= 0:
            return True
        if url.find("amazon-adsystem.com") >= 0:
            return True
        if url.find("googlesyndication") >= 0:
            return True
        if url.find("www.googletagmanager.com") >= 0:
            return True
        if url.find("google-analytics") >= 0:
            return True
        if url.find("googletagservices") >= 0:
            return True
        if url.find("cdn.speedcurve.com") >= 0:
            return True
        if url.find("amazonaws.com") >= 0:
            return True
        if url.find("consent.cookiebot.com") >= 0:
            return True
        if url.find("cloudfront.net") >= 0:
            return True
        if url.find("prg.smartadserver.com") >= 0:
            return True
        if url.find("ads.us.e-planning.net") >= 0:
            return True
        if url.find("static.ads-twitter.com") >= 0:
            return True
        if url.find("analytics.twitter.com") >= 0:
            return True
        if url.find("static.cloudflareinsights.com") >= 0:
            return True

    def is_link_service(self):
        url = self.get_domain_only()

        if not url:
            return False

        if url.find("lmg.gg") >= 0:
            return True
        if url.find("geni.us") >= 0:
            return True
        if url.find("tinyurl.com") >= 0:
            return True
        if url.find("bit.ly") >= 0:
            return True
        if url.find("ow.ly") >= 0:
            return True
        if url.find("adfoc.us") >= 0:
            return True
        if url.endswith("link.to"):
            return True
        if url.find("mailchi.mp") >= 0:
            return True
        if url.find("dbh.la") >= 0:
            return True
        if url.find("ffm.to") >= 0:
            return True
        if url.find("kit.co") >= 0:
            return True
        if url.find("utm.io") >= 0:
            return True
        if url.find("tiny.pl") >= 0:
            return True
        if url.find("reurl.cc") >= 0:
            return True

        # shortcuts
        if url.find("amzn.to") >= 0:
            return True

        return False

    def is_link(self):
        return self.get_type_for_link() == URL_TYPE_HTML

    def get_type_for_link(self):
        the_type = self.get_type_by_ext()
        if the_type:
            return the_type

        ext = self.get_page_ext()
        if not ext:
            return URL_TYPE_HTML

        return URL_TYPE_UNKNOWN

    def is_media(self):
        """
        TODO - crude, hardcoded
        """
        ext = self.get_page_ext()
        if not ext:
            return False

        ext_mapping = [
            "mp3",
            "mp4",
            "avi",
            "ogg",
            "flac",
            "rmvb",
            "wmv",
            "wma",
        ]

        return ext in ext_mapping

    def is_html(self):
        return self.get_type() == URL_TYPE_HTML

    def is_rss(self):
        return self.get_type() == URL_TYPE_RSS

    def get_type(self):
        the_type = self.get_type_by_ext()
        if the_type:
            return the_type

        ext = self.get_page_ext()
        if not ext:
            return URL_TYPE_HTML

        return ext

    def get_type_by_ext(self):
        """
        TODO - crude, hardcoded
        """
        if self.is_analytics():
            return

        ext_mapping = {
            "css": URL_TYPE_CSS,
            "js": URL_TYPE_JAVASCRIPT,
            "html": URL_TYPE_HTML,
            "htm": URL_TYPE_HTML,
            "php": URL_TYPE_HTML,
            "aspx": URL_TYPE_HTML,
            "woff2": URL_TYPE_FONT,
            "tff": URL_TYPE_FONT,
        }

        ext = self.get_page_ext()
        if ext:
            if ext in ext_mapping:
                return ext_mapping[ext]

        # if not found, we return none

    def get_robots_txt_url(self):
        return self.get_domain() + "/robots.txt"

    def is_link_in_domain(self, address):
        if not address.startswith(self.get_domain()):
            return False
        return True

    def split(self):
        result = []
        parts = self.parse_url()

        if len(parts) > 2:
            # protocol + sep + domain
            result.extend(parts[0:3])

        if len(parts) > 3:
            for part in parts[3:]:
                if part.startswith("\\"):
                    part = part[1:]
                if part.startswith("/"):
                    part = part[1:]
                if part.endswith("\\"):
                    part = part[:-1]
                if part.endswith("/"):
                    part = part[:-1]

                if part.find("\\") >= 0:
                    result.extend(part.split("\\"))
                elif part.find("/") >= 0:
                    result.extend(part.split("/"))
                else:
                    result.append(part)

        return result

    def join(self, parts):
        result = ""

        result = parts[0] + parts[1] + parts[2]

        for part in parts[3:]:
            if result.endswith("/"):
                result = result[:-1]
            if result.endswith("\\"):
                result = result[:-1]

            if part.startswith("/"):
                part = part[1:]
            if part.startswith("\\"):
                part = part[1:]

            if part.endswith("/"):
                part = part[:-1]
            if part.endswith("\\"):
                part = part[:-1]

            if part.startswith("?") or part.startswith("#"):
                result = result + part
            else:
                result = result + "/" + part

        return result

    def get_params(self):
        parsed_url = urlparse(self.url)
        params = parse_qs(parsed_url.query)
        return params
