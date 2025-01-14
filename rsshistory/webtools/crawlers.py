"""
Provides cralwers implmenetation that can be used directly in program.

Some crawlers / scrapers cannot be easily called from a thread, etc, because of asyncio.
"""

import json
import traceback
from pathlib import Path
import os
import subprocess
import threading

from utils.dateutils import DateUtils
from utils.basictypes import fix_path_for_os

from .webtools import (
    PageResponseObject,
    WebLogger,
    get_request_to_bytes,
    get_response_from_bytes,
    PAGE_TOO_BIG_BYTES,
    HTTP_STATUS_CODE_EXCEPTION,
    HTTP_STATUS_CODE_CONNECTION_ERROR,
    HTTP_STATUS_CODE_TIMEOUT,
    HTTP_STATUS_CODE_FILE_TOO_BIG,
    HTTP_STATUS_CODE_PAGE_UNSUPPORTED,
    HTTP_STATUS_CODE_SERVER_ERROR,
)
from .pages import (
    RssPage,
    HtmlPage,
)

from .ipc import (
    string_to_command,
)

selenium_feataure_enabled = True
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.common.exceptions import TimeoutException

    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
except Exception as E:
    print(str(E))
    selenium_feataure_enabled = False


class CrawlerInterface(object):
    def __init__(self, request, response_file=None, settings=None):
        """
        @param response_file If set, response is stored in a file
        @param settings passed settings
        """
        self.request = request
        self.response = None
        self.response_file = response_file
        self.settings = settings

        if self.request.timeout_s and settings and "timeout_s" in settings:
            self.timeout_s = max(self.request.timeout_s, settings["timeout_s"])
        elif self.request.timeout_s:
            self.timeout_s = self.request.timeout_s
        elif settings and "timeout_s" in settings:
            self.timeout_s = settings["timeout_s"]
        else:
            self.timeout_s = 10

    def run(self):
        """
         - does its job
         - sets self.response
         - clears everything from memory, it created

        if crawler can access web, then should return response (may be invalid)

        @return response, None if feature is not available
        """
        return self.response

    def response_to_bytes(self):
        all_bytes = bytearray()

        if not self.response:
            return all_bytes

        # same as PageResponseObject
        bytes1 = string_to_command("PageResponseObject.__init__", "OK")
        all_bytes.extend(bytes1)
        bytes2 = string_to_command("PageResponseObject.url", self.response.url)
        all_bytes.extend(bytes2)

        if self.response and self.response.request_url:
            thebytes = string_to_command(
                "PageResponseObject.request_url", self.response.request_url
            )
            all_bytes.extend(thebytes)

        bytes4 = string_to_command(
            "PageResponseObject.status_code", str(self.response.status_code)
        )
        all_bytes.extend(bytes4)

        if self.response and self.response.text:
            bytes5 = string_to_command("PageResponseObject.text", self.response.text)
            all_bytes.extend(bytes5)

        bytes6 = string_to_command(
            "PageResponseObject.headers", json.dumps(self.response.headers)
        )
        all_bytes.extend(bytes6)

        bytes7 = string_to_command("PageResponseObject.__del__", "OK")
        all_bytes.extend(bytes7)

        return all_bytes

    def get_response(self):
        return self.response

    def save_response(self):
        if not self.response:
            if self.request:
                WebLogger.error(
                    "Url:{} Have not received response".format(self.request.url)
                )
            else:
                WebLogger.error("Have not received response")
            return False

        all_bytes = self.response_to_bytes()

        if self.response_file:
            self.save_response_file(self.response_file)

        if self.settings and "remote_server" in self.settings:
            self.save_response_remote(self.settings["remote_server"])

        return True

    def save_response_file(self, file_name):
        if file_name:
            return

        path = Path(self.response_file)
        if not path.parent.exists():
            path.parent.mkdir(parents=True, exist_ok=True)

        with open(self.response_file, "wb") as fh:
            fh.write(all_bytes)

    def save_response_remote(self, remote_server):
        import requests

        if not self.response:
            return

        payload = {}
        payload["url"] = self.response.url
        payload["request_url"] = self.response.request_url
        payload["Contents"] = self.response.get_text()
        payload["Headers"] = self.response.get_headers()
        payload["status_code"] = self.response.status_code

        try:
            response = requests.post(remote_server, json=payload)

            if response.status_code == 200:
                print("Response successfully sent to the remote server.")
                return response.json()  # Assuming the server responds with JSON
            else:
                print(f"Failed to send response. Status code: {response.status_code}")
                print(f"Response text: {response.text}")
                return None
        except requests.RequestException as e:
            # Handle any exceptions raised by the requests library
            print(f"An error occurred while sending the response: {e}")
            return None

    def is_valid(self):
        return False

    def close(self):
        pass

    def get_main_path(self):
        file_path = os.path.realpath(__file__)
        full_path = Path(file_path)
        return full_path.parents[2]


class RequestsCrawler(CrawlerInterface):
    """
    Python requests
    """
    default_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Charset": "utf-8,ISO-8859-1;q=0.7,*;q=0.3",
        "Accept-Encoding": "none",
        "Accept-Language": "en-US,en;q=0.8",
        "Connection": "keep-alive",
    }

    def run(self):
        if not self.is_valid():
            return

        import requests

        WebLogger.debug("Requests Driver:{}".format(self.request.url))

        """
        stream argument allows us to read header before we fetch the page.
        SSL verification makes everything to work slower.
        """

        self.response = PageResponseObject(
            self.request.url,
            text=None,
            status_code=HTTP_STATUS_CODE_EXCEPTION,
            request_url=self.request.url,
        )

        try:
            request_result = self.build_requests()

            if not request_result:
                return self.response

            self.response = PageResponseObject(
                url=request_result.url,
                text="",
                status_code=request_result.status_code,
                headers=dict(request_result.headers),
                request_url=self.request.url,
            )
            if not self.response.is_valid():
                return self.response

            content_length = self.response.get_content_length()
            if content_length > PAGE_TOO_BIG_BYTES:
                self.response.status_code = status_code = HTTP_STATUS_CODE_FILE_TOO_BIG
                self.response.add_error("Page is too big")
                return self.response

            if self.request.ping:
                return self.response

            # TODO do we want to check also content-type?

            content_type = self.response.get_content_type()

            if content_type and not self.response.is_content_type_supported():
                self.response.status_code = HTTP_STATUS_CODE_PAGE_UNSUPPORTED
                self.response.add_error(
                    "Url:{} is not supported {}".format(self.request.url, content_type)
                )
                return self.response

            """
            IF we do not know the content type, or content type is supported
            """
            encoding = self.get_encoding(request_result, self.response)
            if encoding:
                request_result.encoding = encoding

            self.response = PageResponseObject(
                url=request_result.url,
                text=request_result.text,
                status_code=request_result.status_code,
                encoding=request_result.encoding,
                headers=dict(request_result.headers),
                binary=request_result.content,
                request_url=self.request.url,
            )

        except requests.Timeout:
            self.response = PageResponseObject(
                self.request.url,
                text=None,
                status_code=HTTP_STATUS_CODE_TIMEOUT,
                request_url=self.request.url,
            )
            self.response.add_error("Url:{} Page timeout".format(self.request.url))

        except TimeoutException:
            self.response = PageResponseObject(
                self.request.url,
                text=None,
                status_code=HTTP_STATUS_CODE_TIMEOUT,
                request_url=self.request.url,
            )
            self.response.add_error("Url:{} Page timeout".format(self.request.url))

        except requests.exceptions.ConnectionError:
            self.response = PageResponseObject(
                self.request.url,
                text=None,
                status_code=HTTP_STATUS_CODE_CONNECTION_ERROR,
                request_url=self.request.url,
            )
            self.response.add_error("Url:{} Connection error".format(self.request.url))

        except Exception as E:
            WebLogger.exc(E, "Url:{} General exception".format(self.request.url))

            self.response = PageResponseObject(
                self.request.url,
                text=None,
                status_code=HTTP_STATUS_CODE_EXCEPTION,
                request_url=self.request.url,
            )
            self.response.add_error("General page exception")

        return self.response

    def get_encoding(self, request_result, response):
        """
        The default assumed content encoding for text/html is ISO-8859-1 aka Latin-1 :( See RFC-2854. UTF-8 was too young to become the default, it was born in 1993, about the same time as HTML and HTTP.
        Use .content to access the byte stream, or .text to access the decoded Unicode stream.

        chardet does not work on youtube RSS feeds.
        apparent encoding does not work on youtube RSS feeds.
        """

        url = self.request.url

        encoding = response.get_content_type_charset()
        if encoding:
            return encoding

        else:
            # There might be several encoding texts, if so we do not know which one to use
            if response.is_content_html():
                p = HtmlPage(url, request_result.text)
                if p.is_valid():
                    if p.get_charset():
                        return p.get_charset()
            if response.is_content_rss():
                p = RssPage(url, request_result.text)
                if p.is_valid():
                    if p.get_charset():
                        return p.get_charset()

            # TODO this might trigger download of a big file
            text = request_result.text.lower()

            if text.count("encoding") == 1 and text.find('encoding="utf-8"') >= 0:
                return "utf-8"
            elif text.count("charset") == 1 and text.find('charset="utf-8"') >= 0:
                return "utf-8"

    def build_requests(self):
        """
        stream argument - will fetch page contents, when we access contents of page.

        Note - sometimes timeout can not work
        https://stackoverflow.com/questions/21965484/timeout-for-python-requests-get-entire-response
        https://stackoverflow.com/questions/53242211/python-requests-timeout-not-working-properly
        """
        import requests

        def request_with_timeout(url, headers, timeout, verify, stream, result):
            try:
                result['response'] = requests.get(
                    url,
                    headers=headers,
                    timeout=timeout,
                    verify=verify,
                    stream=stream,
                )
            except Exception as e:
                result['exception'] = e

        def make_request_with_threading(url, headers, timeout_s, ssl_verify, stream):
            result = {'response': None, 'exception': None}

            thread = threading.Thread(
                target=request_with_timeout,
                args=(url, headers, timeout_s, ssl_verify, stream, result),
            )
            thread.start()
            thread.join(timeout_s)
            
            if thread.is_alive():
                raise TimeoutException("Request timed out")
            if result['exception']:
                raise result['exception']
            return result['response']

        headers = self.request.headers
        if not headers:
            headers = RequestsCrawler.default_headers

        response = make_request_with_threading(
            url=self.request.url,
            headers=headers,
            timeout_s=self.timeout_s,
            ssl_verify=self.request.ssl_verify,
            stream=True,
        )
        if response:
            return response

    def is_valid(self):
        try:
            import requests

            return True
        except Exception as E:
            print(str(E))
            return False


class RemoteServerCrawler(CrawlerInterface):
    """
    Server that accepts GET and POST requests, runs requests and returns data via JSON response
    """
    def run(self):
        import requests

        if not self.is_valid():
            return

        server_url = self.settings["remote_server"]
        self.settings["crawler"] = self.settings["crawler"]

        crawler_data = {
                "crawler" : self.settings["crawler"],
                "name" : self.settings["name"],
                "timeout" : self.request.timeout_s,
                "settings" : self.settings,
        }

        crawler_data = json.dumps(crawler_data)

        try:
            link = "{}?url={}&crawler_data={}".format(server_url, self.request.url, crawler_data)
            print(link)

            response = requests.get(
                link,
                timeout=self.request.timeout_s,
                verify=False,
                stream=True,
            )

            json_data = self.unpack_data(response.text)

            self.response = PageResponseObject(
                self.request.url,
                text=json_data["contents"],
                status_code=json_data["status_code"],
                request_url=self.request.url,
            )

        except requests.Timeout:
            self.response = PageResponseObject(
                self.request.url,
                text=None,
                status_code=HTTP_STATUS_CODE_TIMEOUT,
                request_url=self.request.url,
            )
            self.response.add_error("Url:{} Page timeout".format(self.request.url))

        except TimeoutException:
            self.response = PageResponseObject(
                self.request.url,
                text=None,
                status_code=HTTP_STATUS_CODE_TIMEOUT,
                request_url=self.request.url,
            )
            self.response.add_error("Url:{} Page timeout".format(self.request.url))

        except requests.exceptions.ConnectionError:
            self.response = PageResponseObject(
                self.request.url,
                text=None,
                status_code=HTTP_STATUS_CODE_CONNECTION_ERROR,
                request_url=self.request.url,
            )
            self.response.add_error("Url:{} Connection error".format(self.request.url))

        except Exception as E:
            WebLogger.exc(E, "Url:{} General exception".format(self.request.url))

            self.response = PageResponseObject(
                self.request.url,
                text=None,
                status_code=HTTP_STATUS_CODE_EXCEPTION,
                request_url=self.request.url,
            )
            self.response.add_error("General page exception")

        return self.response

    def unpack_data(self, input_data):
        json_data = {}

        data = json.loads(input_data)

        # TODO make it cleaner
        if data and len(data) > 2 and "data" in data[3]:
            json_data["status_code"] = data[3]["data"]["status_code"]
        if data and len(data) > 1 and "data" in data[1]:
            json_data["contents"] = data[1]["data"]["Contents"]
        if data and len(data) > 3 and "data" in data[3]:
            json_data["Content-Length"] = data[3]["data"]["Content-Length"]
        if data and len(data) > 3 and "data" in data[3]:
            json_data["Content-Type"] = data[3]["data"]["Content-Type"]

        return json_data

    def is_valid(self):
        try:
            import requests

            return True
        except Exception as E:
            print(str(E))
            return False


class StealthRequestsCrawler(CrawlerInterface):
    """
    Python steath requests
    """

    def run(self):
        if not self.is_valid():
            return

        self.response = PageResponseObject(
            self.request.url,
            text=None,
            status_code=HTTP_STATUS_CODE_EXCEPTION,
            request_url=self.request.url,
        )

        import stealth_requests as requests

        answer = requests.get(
            self.request.url,
            timeout=self.timeout_s,
            verify=self.request.ssl_verify,
            stream=True,
        )

        # text = answer.text_content()
        content = answer.content

        if answer and content:
            self.response = PageResponseObject(
                self.request.url,
                binary=content,
                status_code=answer.status_code,
                request_url=self.request.url,
            )

            return self.response

        elif answer:
            self.response = PageResponseObject(
                self.request.url,
                binary=None,
                text=None,
                status_code=answer.status_code,
                request_url=self.request.url,
            )

            return self.response

    def is_valid(self):
        try:
            import stealth_requests as requests

            return True
        except Exception as E:
            print(str(E))
            return False


class SeleniumDriver(CrawlerInterface):
    """
    Everybody uses selenium
    """

    def __init__(
        self,
        request,
        response_file=None,
        driver_executable=None,
        settings=None,
    ):
        if (
            settings
            and "driver_executable" in settings
            and settings["driver_executable"]
        ):
            driver_executable = settings["driver_executable"]

        super().__init__(
            request,
            response_file=response_file,
            settings=settings,
        )
        self.driver = None
        self.driver_executable = driver_executable

        try:
            self.display = None
            # requires xvfb
            # import os
            # os.environ["DISPLAY"] = ":10.0"
            # from pyvirtualdisplay import Display
            # self.display = Display(visible=0, size=(800, 600))
            # self.display.start()
        except Exception as E:
            print("Str: {}".format(E))

    def get_driver(self):
        """
        https://www.lambdatest.com/blog/internationalization-with-selenium-webdriver/

        locale="en-US"

        For chrome
        options.add_argument("--lang={}".format(locale))

        # For firefox:
        profile = webdriver.FirefoxProfile()
        profile.set_preferences("intl.accept_languages", locale)
        profile.update_preferences()
        """
        raise NotImplementedError("Provide selenium driver implementation!")

    def get_selenium_status_code(self, driver):
        status_code = 200
        try:
            logs = driver.get_log("performance")
            status_code2 = self.get_selenium_status_code_from_logs(logs)
            if status_code2:
                status_code = status_code2
        except Exception as E:
            WebLogger.exc(E, "Chrome webdrider error.")
        return status_code

    def get_selenium_status_code_from_logs(self, logs):
        """
        https://stackoverflow.com/questions/5799228/how-to-get-status-code-by-using-selenium-py-python-code
        TODO should we use selenium wire?

        TODO this probably does not work "Correctly"
        """
        last_status_code = 200
        for log in logs:
            if log["message"]:
                d = json.loads(log["message"])

                content_type = ""
                try:
                    content_type = d["message"]["params"]["response"]["headers"][
                        "content-type"
                    ]
                except Exception as E:
                    pass
                try:
                    content_type = d["message"]["params"]["response"]["headers"][
                        "Content-Type"
                    ]
                except Exception as E:
                    pass

                try:
                    response_received = (
                        d["message"]["method"] == "Network.responseReceived"
                    )
                    if content_type.find("text/html") >= 0 and response_received:
                        last_status_code = d["message"]["params"]["response"]["status"]
                except Exception as E:
                    # we expect that some contents do not have this
                    pass

        return last_status_code

    def get_selenium_headers(self, driver):
        headers = {}
        try:
            logs = driver.get_log("performance")
            headers = self.get_selenium_headers_logs(logs)
            return headers
        except Exception as E:
            WebLogger.exc(E, "Chrome webdrider error")

        return headers

    def get_selenium_headers_logs(self, logs):
        """
        https://stackoverflow.com/questions/5799228/how-to-get-status-code-by-using-selenium-py-python-code
        TODO should we use selenium wire?
        """
        headers = {}
        for log in logs:
            if log["message"]:
                d = json.loads(log["message"])

                content_type = ""
                try:
                    headers = d["message"]["params"]["response"]["headers"]
                except Exception as E:
                    pass

        return headers

    def close(self):
        try:
            if self.driver:
                self.driver.close()
        except Exception as E:
            WebLogger.error(str(E))  # TODO
            WebLogger.debug(str(E))

        try:
            if self.driver:
                self.driver.quit()
        except Exception as E:
            WebLogger.error(str(E))  # TODO
            WebLogger.debug(str(E))

        try:
            if self.display:
                self.display.stop()
        except Exception as E:
            WebLogger.error(str(E))  # TODO
            WebLogger.debug(str(E))


class SeleniumChromeHeadless(SeleniumDriver):
    """
    Selenium chrome headless
    """

    def get_driver(self):
        try:
            # if not self.driver_executable:
            #    self.driver_executable = "/usr/bin/chromedriver"

            if self.driver_executable:
                p = Path(self.driver_executable)
                if not p.exists():
                    WebLogger.error("We do not have chromedriver executable")
                    return

                service = Service(executable_path=self.driver_executable)
            else:
                service = Service()

            options = webdriver.ChromeOptions()
            options.add_argument("--headless")
            options.add_argument("--lang={}".format("en-US"))

            options.set_capability("goog:loggingPrefs", {"performance": "ALL"})

            driver = webdriver.Chrome(service=service, options=options)
            return driver
        except Exception as E:
            print(str(E))
            error_text = traceback.format_exc()
            WebLogger.debug(
                "Cannot obtain driver:{}\n{}".format(self.request.url, error_text)
            )

    def run(self):
        """
        To obtain RSS page you have to run real, full blown browser.

        Headless might not be enough to fool cloudflare.
        """
        if not self.is_valid():
            return

        self.driver = self.get_driver()
        if not self.driver:
            return

        self.response = PageResponseObject(
            self.request.url,
            text=None,
            status_code=HTTP_STATUS_CODE_EXCEPTION,
            request_url=self.request.url,
        )

        WebLogger.debug("SeleniumChromeHeadless Driver:{}".format(self.request.url))

        try:
            # add 10 seconds for start of browser, etc.
            selenium_timeout = self.timeout_s

            self.driver.set_page_load_timeout(selenium_timeout)

            self.driver.get(self.request.url)
            """
            TODO - if webpage changes link, it should also update it in this object
            """

            status_code = self.get_selenium_status_code(self.driver)

            headers = self.get_selenium_headers(self.driver)
            WebLogger.debug("Selenium headers:{}\n{}".format(self.request.url, headers))

            html_content = self.driver.page_source

            # TODO use selenium wire to obtain status code & headers?

            self.response = PageResponseObject(
                self.driver.current_url,
                text=html_content,
                status_code=status_code,
                request_url=self.request.url,
            )
        except TimeoutException:
            error_text = traceback.format_exc()
            WebLogger.debug("Page timeout:{}\n{}".format(self.request.url, error_text))
            self.response = PageResponseObject(
                self.request.url,
                text=None,
                status_code=HTTP_STATUS_CODE_TIMEOUT,
                request_url=self.request.url,
            )
        except Exception as E:
            WebLogger.exc(E, "Url:{}".format(self.request.url))
            self.response = PageResponseObject(
                self.request.url,
                text=None,
                status_code=HTTP_STATUS_CODE_EXCEPTION,
                request_url=self.request.url,
            )

        return self.response

    def is_valid(self):
        return selenium_feataure_enabled


class SeleniumChromeFull(SeleniumDriver):
    """
    Selenium chrome full - TODO
    """

    def get_driver(self):
        """
        https://forums.raspberrypi.com/viewtopic.php?t=129320
        """
        try:
            if self.driver_executable:
                p = Path(self.driver_executable)
                if not p.exists():
                    WebLogger.error("We do not have chromedriver executable")
                    return

            if self.driver_executable:
                service = Service(executable_path=str(self.driver_executable))
            else:
                service = Service()

            try:
                # requires xvfb
                import os

                os.environ["DISPLAY"] = ":10.0"
                from pyvirtualdisplay import Display

                self.display = Display(visible=0, size=(800, 600))
                self.display.start()
            except Exception as E:
                print("Str: {}".format(E))

            options = webdriver.ChromeOptions()
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--lang={}".format("en-US"))

            # path = "./linklibrary/rsshistory/static/extensions/chrome/ublock_1.61.2_0.crx"
            # options.add_extension(path)

            options.add_argument("start-maximized")
            options.add_argument("disable-infobars")
            options.add_argument("--disable-extensions")
            options.add_argument("--disable-gpu")

            # options to enable performance log, to read status code
            options.set_capability("goog:loggingPrefs", {"performance": "ALL"})

            return webdriver.Chrome(service=service, options=options)
        except Exception as E:
            WebLogger.exc("Cannot obtain driver:{}\n{}".format(E, self.request.url))

    def run(self):
        """
        To obtain RSS page you have to run real, full blown browser.

        It may require some magic things to make the browser running.

        https://stackoverflow.com/questions/50642308/webdriverexception-unknown-error-devtoolsactiveport-file-doesnt-exist-while-t
        """
        if not self.is_valid():
            return

        self.driver = self.get_driver()
        if not self.driver:
            return

        self.response = PageResponseObject(
            self.request.url,
            text=None,
            status_code=HTTP_STATUS_CODE_EXCEPTION,
            request_url=self.request.url,
        )

        WebLogger.debug("SeleniumChromeFull Driver:{}".format(self.request.url))

        try:
            # add 10 seconds for start of browser, etc.
            selenium_timeout = self.timeout_s

            self.driver.set_page_load_timeout(selenium_timeout)

            self.driver.get(self.request.url)

            status_code = self.get_selenium_status_code(self.driver)

            """
            TODO - if webpage changes link, it should also update it in this object
            """

            page_source = self.driver.page_source

            self.response = PageResponseObject(
                self.driver.current_url,
                text=page_source,
                status_code=status_code,
                request_url=self.request.url,
            )

        except TimeoutException:
            error_text = traceback.format_exc()
            WebLogger.debug("Page timeout:{}\n{}".format(self.request.url, error_text))
            self.response = PageResponseObject(
                self.request.url,
                text=None,
                status_code=HTTP_STATUS_CODE_TIMEOUT,
                request_url=self.request.url,
            )
        except Exception as E:
            WebLogger.exc(E, "Url:{}".format(self.request.url))
            self.response = PageResponseObject(
                self.request.url,
                text=None,
                status_code=HTTP_STATUS_CODE_EXCEPTION,
                request_url=self.request.url,
            )

        return self.response

    def is_valid(self):
        return selenium_feataure_enabled


class SeleniumUndetected(SeleniumDriver):
    """
    Selenium undetected
    """

    def get_driver(self):
        try:
            """
            NOTE: This driver may not work on raspberry PI
            """
            import undetected_chromedriver as uc

            options = uc.ChromeOptions()
            options.set_capability("goog:loggingPrefs", {"performance": "ALL"})
            options.add_argument("--lang={}".format("en-US"))
            return uc.Chrome(options=options)
        except Exception as E:
            error_text = traceback.format_exc()
            WebLogger.debug(
                "Cannot obtain driver:{}\n{}".format(self.request.url, error_text)
            )
            return

    def run(self):
        """
        To obtain RSS page you have to run real, full blown browser.

        It may require some magic things to make the browser running.

        This does not work on raspberry pi
        """
        if not self.is_valid():
            return

        self.driver = self.get_driver()
        if not self.driver:
            return

        self.response = PageResponseObject(
            self.request.url,
            text=None,
            status_code=HTTP_STATUS_CODE_EXCEPTION,
            request_url=self.request.url,
        )

        WebLogger.debug("SeleniumUndetected Driver:{}".format(self.request.url))

        try:
            # add 10 seconds for start of browser, etc.
            selenium_timeout = self.timeout_s

            self.driver.set_page_load_timeout(selenium_timeout)

            self.driver.get(self.request.url)

            status_code = self.get_selenium_status_code(self.driver)

            """
            TODO - if webpage changes link, it should also update it in this object
            """

            page_source = self.driver.page_source

            self.response = PageResponseObject(
                self.driver.current_url,
                text=page_source,
                status_code=status_code,
                request_url=self.request.url,
            )

        except TimeoutException:
            error_text = traceback.format_exc()
            WebLogger.debug("Page timeout:{}\n{}".format(self.request.url, error_text))
            self.response = PageResponseObject(
                self.request.url,
                text=None,
                status_code=HTTP_STATUS_CODE_TIMEOUT,
                request_url=self.request.url,
            )

        return self.response

    def is_valid(self):
        try:
            import undetected_chromedriver as uc

            return True
        except Exception as E:
            return False


class ScriptCrawler(CrawlerInterface):
    """
    Used to run script to obtain URL response.
    Calls script, and receives reply in the file.

    Note:
     If we have multiple instances/workspaces each can write their own output file
    """

    def __init__(
        self,
        request,
        response_file=None,
        cwd=None,
        script=None,
        settings=None,
    ):
        if settings and "script" in settings and settings["script"]:
            script = settings["script"]

        super().__init__(
            request=request,
            response_file=response_file,
            settings=settings,
        )
        self.cwd = cwd
        self.script = script

        if "cwd" in self.settings:
            self.cwd = self.settings["cwd"]

        if not self.cwd:
            self.cwd = self.get_main_path()

        if not self.response_file:
            from .webconfig import WebConfig

            if WebConfig.script_responses_directory is not None:
                response_dir = Path(WebConfig.script_responses_directory)
            else:
                response_dir = Path("storage")

            self.response_file = (
                self.get_main_path() / response_dir / self.get_response_file_name()
            )

    def run(self):
        if not self.is_valid():
            return

        self.response = PageResponseObject(
            self.request.url,
            text=None,
            status_code=HTTP_STATUS_CODE_EXCEPTION,
            request_url=self.request.url,
        )

        response_file_location = Path(self.response_file)

        if len(response_file_location.parents) > 1:
            response_dir = response_file_location.parents[1]
            if not response_dir.exists():
                response_dir.mkdir(parents=True, exist_ok=True)

        file_abs = response_file_location
        if file_abs.exists():
            file_abs.unlink()

        script = self.script + ' --url "{}" --output-file="{}" --timeout={}'.format(
            self.request.url, self.response_file, self.timeout_s
        )

        # WebLogger.error("Response:{}".format(self.response_file))
        # WebLogger.error("CWD:{}".format(self.cwd))
        # WebLogger.error("maintl:{}".format(self.get_main_path()))
        # WebLogger.error("script:{}".format(script))

        try:
            p = subprocess.run(
                script,
                shell=True,
                capture_output=True,
                cwd=self.cwd,
                timeout=self.timeout_s + 10,  # add more time for closing browser, etc
            )
        except subprocess.TimeoutExpired as E:
            WebLogger.debug(E, "Timeout on running script")

            self.response = PageResponseObject(
                self.request.url,
                text=None,
                status_code=HTTP_STATUS_CODE_TIMEOUT,
                request_url=self.request.url,
            )
            return self.response
        except ValueError as E:
            WebLogger.exc(E, "Incorrect script call {}".format(script))
            return self.response

        if p.returncode != 0:
            if p.stdout:
                stdout_str = p.stdout.decode()
                if stdout_str != "":
                    WebLogger.error(stdout_str)

            if p.stderr:
                stderr_str = p.stderr.decode()
                if stderr_str and stderr_str != "":
                    WebLogger.error("Url:{}. {}".format(self.request.url, stderr_str))

            WebLogger.error(
                "Url:{}. Script:'{}'. Return code invalid:{}. Path:{}".format(
                    self.request.url,
                    script,
                    p.returncode,
                    self.cwd,
                )
            )

        if file_abs.exists():
            response = None

            with open(str(file_abs), "rb") as fh:
                all_bytes = fh.read()
                self.response = get_response_from_bytes(all_bytes)

            file_abs.unlink()

            return self.response

        else:
            WebLogger.error(
                "Url:{}. Response file does not exist:{}".format(
                    self.request.url, str(response_file_location)
                )
            )

            self.response = PageResponseObject(
                self.request.url,
                text=None,
                status_code=HTTP_STATUS_CODE_SERVER_ERROR,
                request_url=self.request.url,
            )

    def process_input(self):
        """
        TODO these three functions below, could be used
        """
        if not self.script:
            self.response_file = None
            self.operating_path = None
            return

        self.operating_path = self.get_operating_dir()
        self.response_file = self.get_response_file_name(self.operating_path)

    def get_response_file_name(self):
        file_name_url_part = fix_path_for_os(self.request.url)
        file_name_url_part = file_name_url_part.replace("\\", "")
        file_name_url_part = file_name_url_part.replace("/", "")
        file_name_url_part = file_name_url_part.replace("@", "")

        response_file = "response_{}.txt".format(file_name_url_part)
        return response_file

    def get_operating_dir(self):
        file_path = os.path.realpath(__file__)
        full_path = Path(file_path)

        if WebConfig.script_operating_dir is None:
            operating_path = full_path.parents[2]
        else:
            operating_path = Path(WebConfig.script_operating_dir)

        if not operating_path.exists():
            WebLogger.error("Operating path does not exist: {}".format(operating_path))
            return

        return operating_path

    def close(self):
        if self.response_file:
            response_file_location = Path(self.response_file)
            if response_file_location.exists():
                response_file_location.unlink()

    def is_valid(self):
        if not self.script:
            return False

        return True


class ServerCrawler(CrawlerInterface):
    """
    Used to ask crawling server for URL.
    Sends request to server, and receives reply
    """

    def __init__(
        self,
        request,
        response_file=None,
        settings=None,
        script=None,
    ):
        if settings and "script" in settings and settings["script"]:
            script = settings["script"]

        super().__init__(
            request=request,
            response_file=response_file,
            settings=settings,
        )
        self.script = script
        self.connection = None

    def run(self):
        if not self.is_valid():
            return

        self.response = PageResponseObject(
            self.request.url,
            text=None,
            status_code=HTTP_STATUS_CODE_EXCEPTION,
            request_url=self.request.url,
        )

        script_time_start = DateUtils.get_datetime_now_utc()

        # TODO implement

        response = PageResponseObject(self.request.url)
        response.status_code = HTTP_STATUS_CODE_TIMEOUT
        response.request_url = self.request.url

        self.response = response

        return self.response

    def close(self):
        if self.connection:
            self.connection.close()

    def is_valid(self):
        if not self.script:
            return False

        return True


class SeleniumBase(CrawlerInterface):
    """
    This is based
    """

    def __init__(
        self,
        request,
        response_file=None,
        driver_executable=None,
        settings=None,
    ):
        super().__init__(
            request=request,
            response_file=response_file,
            settings=settings,
        )

    def run(self):
        if not self.is_valid():
            return

        self.response = PageResponseObject(
            self.request.url,
            text=None,
            status_code=HTTP_STATUS_CODE_EXCEPTION,
            request_url=self.request.url,
        )

        try:
            from seleniumbase import SB
        except Exception as E:
            return self.response

        with SB() as sb:
            sb.open(request.url)
            page_source = sb.get_page_source()

            response = webtools.PageResponseObject(request.url)
            # TODO obtain url from SB
            # TODO obtain headers from SB
            # TODO obtain status code from SB
            response.request_url = request.url

            response.set_text(page_source)

            return response

    def is_valid(self):
        return True
