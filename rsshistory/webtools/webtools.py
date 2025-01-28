"""
This file should not include any other or django related files.

#1
Do not harm anyone. Write ethical programs, and scrapers.

#2
By default SSL verification is disabled. Speeds up processing. At least in my experience.

SSL is mostly important for interacting with pages, not when web scraping. I think. I am not an expert.

#3
If SSL verification is disabled you can see contents of your own domain:
https://support.bunny.net/hc/en-us/articles/360017484759-The-CDN-URLs-are-returning-redirects-back-to-my-domain

Other notes:
 - Sometimes we see the CDN URLs return a 301 redirect back to your own website.
   Usually, when this happens, it's caused by a misconfiguration of your origin server and the origin URL of your pull zone. If the origin URL sends back a redirect, our servers will simply forward that to the user.
 - 403 status code means that your user agent is incorrect / prohibited
 - other statuses can also mean that your user agent is rejected (rarely / edge cases)
 - content-type in headers can be incorrectly set. Found one RSS file that had "text/html"
 - I rely on tools. Those tools have problems/issues. Either we can live with that, or you would have to implement every dependency

TODO:
    - selenium and other drivers should be created once, then only asked for urls. Currently they are re-created each time we ask for a page
    - currently there is a hard limit for file size. If page is too big, it is just skipped
    - we should check meta info before obtaining entire file. Currently it is not done so. Encoding may be read from file, in some cases
    - maybe lists of mainstream media, or link services could be each in one class. Configurable, so that it can be overriden

Main classes are:
    - Url - most things should be done through it
    - PageOptions - upper layers should decide how a page should be called. Supplied to Url
    - PageRequestObject - request
    - PageResponseObject - page response, interface for all implementations
"""

import hashlib
import html
import traceback
import re
import json
from dateutil import parser
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup

from utils.dateutils import DateUtils

__version__ = "0.0.5"


PAGE_TOO_BIG_BYTES = 5000000  # 5 MB. There are some RSS more than 1MB


URL_TYPE_RSS = "rss"
URL_TYPE_CSS = "css"
URL_TYPE_JAVASCRIPT = "javascript"
URL_TYPE_HTML = "html"
URL_TYPE_FONT = "font"
URL_TYPE_UNKNOWN = "unknown"

HTTP_STATUS_CODE_EXCEPTION = 600
HTTP_STATUS_CODE_CONNECTION_ERROR = 603
HTTP_STATUS_CODE_TIMEOUT = 604
HTTP_STATUS_CODE_FILE_TOO_BIG = 612
HTTP_STATUS_CODE_PAGE_UNSUPPORTED = 613
HTTP_STATUS_CODE_SERVER_ERROR = 614


class WebLogger(object):
    """
    Logging interface
    """

    web_logger = None

    def info(info_text, detail_text="", user=None, stack=False):
        if WebLogger.web_logger:
            WebLogger.web_logger.info(info_text, detail_text, user, stack)

    def debug(info_text, detail_text="", user=None, stack=False):
        if WebLogger.web_logger:
            WebLogger.web_logger.debug(info_text, detail_text, user, stack)

    def warning(info_text, detail_text="", user=None, stack=False):
        if WebLogger.web_logger:
            WebLogger.web_logger.warning(info_text, detail_text, user, stack)

    def error(info_text, detail_text="", user=None, stack=False):
        if WebLogger.web_logger:
            WebLogger.web_logger.error(info_text, detail_text, user, stack)

    def notify(info_text, detail_text="", user=None):
        if WebLogger.web_logger:
            WebLogger.web_logger.notify(info_text, detail_text, user, stack)

    def exc(exception_object, info_text=None, user=None):
        if WebLogger.web_logger:
            WebLogger.web_logger.exc(exception_object, info_text)


def status_code_to_text(status_code):
    if not status_code:
        return ""

    if status_code == 200:
        return "HTTP_STATUS_OK(200)"
    elif status_code == 403:
        return "HTTP_STATUS_USER_AGENT(403)"
    elif status_code == 600:
        return "HTTP_STATUS_CODE_EXCEPTION(600)"
    elif status_code == 603:
        return "HTTP_STATUS_CODE_CONNECTION_ERROR(603)"
    elif status_code == 604:
        return "HTTP_STATUS_CODE_TIMEOUT(604)"
    elif status_code == 612:
        return "HTTP_STATUS_CODE_FILE_TOO_BIG(612)"
    elif status_code == 613:
        return "HTTP_STATUS_CODE_PAGE_UNSUPPORTED(613)"
    elif status_code == 614:
        return "HTTP_STATUS_CODE_SERVER_ERROR(614)"
    else:
        return str(status_code)


def lazy_load_content(func):
    """
    Lazy load for functions.
    We do not want page contents during construction.
    We want it only when necessary.
    """

    def wrapper(self, *args, **kwargs):
        if not self.response:
            self.response = self.get_response()
        return func(self, *args, **kwargs)

    return wrapper


def date_str_to_date(date_str):
    if date_str:
        wh = date_str.find("Published:")
        if wh >= 0:
            wh = date_str.find(":", wh)
            date_str = date_str[wh + 1 :].strip()

        try:
            parsed_date = parser.parse(date_str)
            return DateUtils.to_utc_date(parsed_date)
        except Exception as E:
            stack_lines = traceback.format_stack()
            stack_str = "".join(stack_lines)

            # we want to know who generated this issue
            detail_text = "Exception Data:{}\nStack:{}".format(str(E), stack_str)

            WebLogger.info(
                "Could not parse date:{}\n".format(date_str),
                detail_text=detail_text,
            )


def calculate_hash(text):
    try:
        return hashlib.md5(text.encode("utf-8")).digest()
    except Exception as E:
        WebLogger.exc(E, "Could not calculate hash")


class PageOptions(object):
    """
    Page request options. Serves more like request API.

    API user defines if headless browser is required.
    WebTools can be configured to use a script, port, or whatever

    Fields:
     - ping - only check status code, and headers of page. Does not download contents
     - browser promotions - if requests cannot receive response we can try with headless or full browser
     - user_agent - not supported by all crawlers. Selenium, stealth requests uses their own agents
     - mode_mapping - configuration of modes
    """

    def __init__(self):
        self.ssl_verify = True
        self.ping = False
        self.use_browser_promotions = (
            True  # tries next mode if normal processing does not work
        )

        self.mode_mapping = {}

        self.user_agent = None  # passed if you wish certain user agent to be used

    def is_mode_mapping(self):
        if self.mode_mapping and len(self.mode_mapping) > 0:
            return True

    def copy_config(self, other_config):
        # if we have mode mapping - use it
        self.mode_mapping = other_config.mode_mapping
        self.ssl_verify = other_config.ssl_verify

    def __str__(self):
        if self.mode_mapping and len(self.mode_mapping) > 0:
            return "Browser:{} P:{} SSL:{} PR:{}".format(
                self.mode_mapping[0],
                self.ping,
                self.ssl_verify,
                self.use_browser_promotions,
            )
        else:
            return "Browser:None P:{} SSL:{} PR:{}".format(
                self.ping,
                self.ssl_verify,
                self.use_browser_promotions,
            )

    def get_str(self):
        return str(self)

    def get_crawler(self, name):
        for mode_data in self.mode_mapping:
            if "enabled" in mode_data:
                if mode_data["name"] == name and mode_data["enabled"] == True:
                    return mode_data
            else:
                if mode_data["name"] == name:
                    return mode_data

    def bring_to_front(self, input_data):
        result = [input_data]
        for mode_data in self.mode_mapping:
            if mode_data == input_data:
                continue

            result.append(mode_data)

        self.mode_mapping = result

    def get_timeout(self, timeout_s):
        if not self.mode_mapping or len(self.mode_mapping) == 0:
            return timeout_s

        first_mode = self.mode_mapping[0]

        if "settings" not in first_mode:
            return timeout_s

        settings = first_mode["settings"]

        if "timeout" in settings:
            timeout_crawler = settings["timeout"]
            return timeout_crawler

        return timeout_s


class PageRequestObject(object):
    """
    Precise information for scraping.
    Should contain information about what is to be scraped. Means of scraping should not be apart of this.

    @example Url, timeout is OK.
    @example Scarping script name, port, is not OK
    """

    def __init__(
        self,
        url,
        headers=None,
        user_agent=None,
        request_headers=None,
        timeout_s=10,
        ping=False,
        ssl_verify=True,
    ):
        self.url = url

        self.user_agent = user_agent

        self.timeout_s = timeout_s
        self.ping = ping
        self.headers = headers
        self.request_headers = request_headers

        self.ssl_verify = True

    def __str__(self):
        return "Url:{} Timeout:{} Ping:{}".format(self.url, self.timeout_s, self.ping)


class PageResponseObject(object):
    STATUS_CODE_OK = 200
    STATUS_CODE_ERROR = 500
    STATUS_CODE_UNDEF = 0

    def __init__(
        self,
        url=None,  # received url
        binary=None,
        text=None,
        status_code=STATUS_CODE_OK,
        encoding=None,
        headers=None,
        request_url=None,
    ):
        """
        @param contents Text

        TODO this should be cleaned up. We should pass binary, and encoding
        """
        self.errors = []
        self.url = url
        self.request_url = request_url
        self.status_code = status_code
        self.crawler_data = None

        self.binary = None
        self.text = None

        if binary:
            self.binary = binary
        if text:
            self.text = text

        # I read selenium always assume utf8 encoding

        # encoding = chardet.detect(contents)['encoding']
        # self.apparent_encoding = encoding
        # self.encoding = encoding

        if not headers:
            self.headers = {}
        else:
            self.headers = headers

        if not self.is_headers_empty():
            charset = self.get_content_type_charset()
            if charset:
                self.encoding = charset
                self.apparent_encoding = charset
            elif encoding:
                self.encoding = encoding
                self.apparent_encoding = encoding
            else:
                self.encoding = "utf-8"
                self.apparent_encoding = "utf-8"
        else:
            self.encoding = encoding
            self.apparent_encoding = encoding

        if not self.encoding:
            self.encoding = "utf-8"
            self.apparent_encoding = "utf-8"

        if self.binary and not self.text:
            try:
                self.text = self.binary.decode(self.encoding)
            except Exception as E:
                WebLogger.exc(
                    E, "Cannot properly decode ansower from {}".format(self.url)
                )
                self.text = self.binary.decode(self.encoding, errors="ignore")

        if self.text and not self.binary:
            try:
                self.binary = self.text.encode(self.encoding)
            except Exception as E:
                WebLogger.exc(
                    E, "Cannot properly encode ansower from {}".format(self.url)
                )
                self.binary = self.text.encode(self.encoding, errors="ignore")

    def is_headers_empty(self):
        return len(self.headers) == 0

    def set_crawler(self, crawler_data):
        self.crawler_data = dict(crawler_data)
        self.crawler_data["crawler"] = type(self.crawler_data["crawler"]).__name__

    def get_content_type(self):
        if "Content-Type" in self.headers:
            return self.headers["Content-Type"]
        if "content-type" in self.headers:
            return self.headers["content-type"]

    def get_last_modified(self):
        date = None

        if "Last-Modified" in self.headers:
            date = self.headers["Last-Modified"]
        if "last-modified" in self.headers:
            date = self.headers["last-modified"]

        if date:
            return date_str_to_date(date)

    def get_content_type_charset(self):
        content = self.get_content_type()
        if not content:
            return

        elements = content.split(";")
        for element in elements:
            wh = element.lower().find("charset")
            if wh >= 0:
                charset_elements = element.split("=")
                if len(charset_elements) > 1:
                    charset = charset_elements[1]

                    if charset.startswith('"') or charset.startswith("'"):
                        return charset[1:-1]
                    else:
                        return charset

    def is_content_html(self):
        content = self.get_content_type()
        if not content:
            return False

        if content.lower().find("html") >= 0:
            return True

    def is_content_image(self):
        content = self.get_content_type()
        if not content:
            return False

        if content.lower().find("image") >= 0:
            return True

    def is_content_rss(self):
        content = self.get_content_type()
        if not content:
            return False

        if content.lower().find("rss") >= 0:
            return True
        if content.lower().find("xml") >= 0:
            return True

    def is_content_json(self):
        content = self.get_content_type()
        if not content:
            return False

        if content.lower().find("json") >= 0:
            return True

    def get_content_length(self):
        if "content-length" in self.headers:
            return int(self.headers["content-length"])
        if "Content-Length" in self.headers:
            return int(self.headers["Content-Length"])

        if self.text:
            return len(self.text)

        if self.binary:
            return len(self.binary)

        return 0

    def is_content_type_supported(self):
        """
        You can preview on a browser headers. Ctr-shift-i on ff
        """
        content_type = self.get_content_type()
        if content_type.find("text") >= 0:
            return True
        if content_type.find("application") >= 0:
            return True
        if content_type.find("xml") >= 0:
            return True

        return False

    def get_redirect_url(self):
        if (
            self.is_this_status_redirect()
            and "Location" in self.headers
            and self.headers["Location"]
        ):
            return self.headers["Location"]

    def is_this_status_ok(self):
        if self.status_code == 0:
            return False

        return self.status_code >= 200 and self.status_code < 300

    def is_this_status_redirect(self):
        """
        HTML code 403 - some pages block you because of your user agent. This code says exactly that.
        https://developer.mozilla.org/en-US/docs/Web/HTTP/Status
        """
        return (
            self.status_code > 300 and self.status_code < 400
        ) or self.status_code == 403

    def is_this_status_nok(self):
        """
        This function informs that status code is so bad, that further communication does not make any sense
        """
        if self.is_this_status_redirect():
            return False

        return self.status_code < 200 or self.status_code >= 400

    def is_valid(self):
        if self.is_this_status_nok():
            return False

        return True

    def get_status_code(self):
        return self.status_code

    def get_text(self):
        return self.text

    def get_binary(self):
        return self.content

    def get_headers(self):
        self.headers["Content-Type"] = self.get_content_type()
        self.headers["Content-Length"] = self.get_content_length()
        self.headers["Charset"] = self.get_content_type_charset()

        return self.headers

    def set_text(self, text, encoding=None):
        if encoding:
            self.encoding = encoding
        else:
            if self.encoding is None:
                self.encoding = "utf-8"

        self.text = text
        self.content = text.encode(self.encoding)

    def set_binary(self, binary, encoding="utf-8"):
        self.content = binary
        self.text = binary.decode(encoding)

    def add_error(self, error_text):
        self.errors.append(error_text)

    def __str__(self):
        has_text_data = "Yes" if self.text else "No"
        has_binary_data = "Yes" if self.binary else "No"

        status_code_text = status_code_to_text(self.status_code)

        return "PageResponseObject: Url:{} Status code:{} Headers:{} Text:{} Binary:{}".format(
            self.url,
            status_code_text,
            self.headers,
            has_text_data,
            has_binary_data,
        )

    def is_html(self):
        if self.get_content_type() is not None and self.is_content_html():
            return True

    def is_rss(self):
        if self.get_content_type() is not None and self.is_content_rss():
            return True

    def is_json(self):
        if self.get_content_type() is not None and self.is_content_json():
            return True

    def is_text(self):
        if (
            self.get_content_type() is not None
            and self.get_content_type().find("text") >= 0
        ):
            return True


def get_request_to_bytes(request, script):
    from .ipc import string_to_command

    total_bytes = bytearray()

    bytes1 = string_to_command("PageRequestObject.__init__", "OK")
    bytes2 = string_to_command("PageRequestObject.url", request.url)
    bytes3 = string_to_command("PageRequestObject.timeout", str(request.timeout_s))
    if request.user_agent != None:
        bytes4 = string_to_command(
            "PageRequestObject.user_agent", str(request.user_agent)
        )
    else:
        bytes4 = bytearray()
    if request.request_headers != None:
        bytes5 = string_to_command(
            "PageRequestObject.request_headers", json.dumps(request.request_headers)
        )
    else:
        bytes5 = bytearray()

    bytes6 = string_to_command("PageRequestObject.ssl_verify", str(request.ssl_verify))
    bytes7 = string_to_command("PageRequestObject.script", script)

    bytes8 = string_to_command("PageRequestObject.__del__", "OK")

    total_bytes.extend(bytes1)
    total_bytes.extend(bytes2)
    total_bytes.extend(bytes3)
    total_bytes.extend(bytes4)
    total_bytes.extend(bytes5)
    total_bytes.extend(bytes6)
    total_bytes.extend(bytes7)
    total_bytes.extend(bytes8)

    return total_bytes


def get_response_to_bytes(response):
    from .ipc import string_to_command

    total_bytes = bytearray()

    bytes1 = string_to_command("PageResponseObject.__init__", "OK")
    bytes2 = string_to_command("PageResponseObject.url", response.url)
    bytes3 = string_to_command(
        "PageResponseObject.status_code", str(response.status_code)
    )
    if response.headers != None:
        bytes4 = string_to_command(
            "PageResponseObject.headers", json.dumps(response.headers)
        )
    else:
        bytes4 = bytearray()

    if response.text:
        bytes5 = string_to_command("PageResponseObject.text", response.text)
    elif response.binary:
        bytes5 = bytes_to_command("PageResponseObject.text", response.binary)
    else:
        bytes5 = bytearray()
    bytes6 = string_to_command(
        "PageResponseObject.request_url", str(response.request_url)
    )
    bytes7 = string_to_command("PageResponseObject.__del__", "OK")

    total_bytes.extend(bytes1)
    total_bytes.extend(bytes2)
    total_bytes.extend(bytes3)
    total_bytes.extend(bytes4)
    total_bytes.extend(bytes5)
    total_bytes.extend(bytes6)
    total_bytes.extend(bytes7)

    return total_bytes


def get_response_from_bytes(all_bytes):
    from .ipc import commands_from_bytes

    response = PageResponseObject("")

    commands_data = commands_from_bytes(all_bytes)
    for command_data in commands_data:
        if command_data[0] == "PageResponseObject.__init__":
            pass
        elif command_data[0] == "PageResponseObject.url":
            response.url = command_data[1].decode()
        elif command_data[0] == "PageResponseObject.request_url":
            response.request_url = command_data[1].decode()
        elif command_data[0] == "PageResponseObject.headers":
            try:
                response.headers = json.loads(command_data[1].decode())
            except ValueError as E:
                WebLogger.exc(E, "Exception when loading headers")
        elif command_data[0] == "PageResponseObject.status_code":
            try:
                response.status_code = int(command_data[1])
            except ValueError as E:
                WebLogger.exc(E, "Exception when loading headers")
        elif command_data[0] == "PageResponseObject.text":
            response.set_text(command_data[1].decode())
        elif command_data[0] == "PageResponseObject.__del__":
            pass

    return response


class InputContent(object):
    def __init__(self, text):
        self.text = text

    def htmlify(self):
        """
        Use iterative approach. There is one thing to keep in mind:
         - text can contain <a href=" links already

        So some links needs to be translated. Some do not.

        @return text with https links changed into real links
        """
        self.text = self.strip_html_attributes()
        self.text = self.linkify("https://")
        self.text = self.linkify("http://")
        return self.text

    def strip_html_attributes(self):
        soup = BeautifulSoup(self.text, "html.parser")

        for tag in soup.find_all(True):
            if tag.name == "a":
                # Preserve "href" attribute for anchor tags
                tag.attrs = {"href": tag.get("href")}
            elif tag.name == "img":
                # Preserve "src" attribute for image tags
                tag.attrs = {"src": tag.get("src")}
            else:
                # Remove all other attributes
                tag.attrs = {}

        self.text = str(soup)
        return self.text

    def linkify(self, protocol="https://"):
        """
        @return text with https links changed into real links
        """
        if self.text.find(protocol) == -1:
            return self.text

        import re

        result = ""
        i = 0

        while i < len(self.text):
            pattern = r"{}\S+(?![\w.])".format(protocol)
            match = re.match(pattern, self.text[i:])
            if match:
                url = match.group()
                # Check the previous 10 characters
                preceding_chars = self.text[max(0, i - 10) : i]

                # We do not care who write links using different char order
                if '<a href="' not in preceding_chars and "<img" not in preceding_chars:
                    result += f'<a href="{url}">{url}</a>'
                else:
                    result += url
                i += len(url)
            else:
                result += self.text[i]
                i += 1

        self.text = result

        return result
