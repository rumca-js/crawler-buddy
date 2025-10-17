"""
Provides cralwers implmenetation that can be used directly in program.

Some crawlers / scrapers cannot be easily called from a thread, etc, because of asyncio.
"""

import json
import traceback
import time
from pathlib import Path
import shutil
import os
import subprocess
import threading
import urllib.parse
import tempfile

from utils.basictypes import fix_path_for_os

from webtoolkit import (
    RssPage,
    HtmlPage,
    PageResponseObject,
    WebLogger,
    CrawlerInterface,
    WebToolsTimeoutException,
    get_response_from_bytes,
    HTTP_STATUS_UNKNOWN,
    HTTP_STATUS_OK,
    HTTP_STATUS_USER_AGENT,
    HTTP_STATUS_TOO_MANY_REQUESTS,
    HTTP_STATUS_CODE_EXCEPTION,
    HTTP_STATUS_CODE_CONNECTION_ERROR,
    HTTP_STATUS_CODE_TIMEOUT,
    HTTP_STATUS_CODE_FILE_TOO_BIG,
    HTTP_STATUS_CODE_PAGE_UNSUPPORTED,
    HTTP_STATUS_CODE_SERVER_ERROR,
)


class SeleniumDriver(CrawlerInterface):
    """
    Everybody uses selenium

    Quirks:
     - status_code cannot be easily read, there is some code that "may" work
     - we may want to wait some time after reading page for javascript to kick in and do it's job
     - full browser may require some additional OS shananigans, for example xvfb

    Note:
     - how can we make for the driver to be persistent? we do not want to start driver again and again
     - we could not be running in parallel new drivers
    """
    counter = 0

    def __init__(
        self,
        request=None,
        url=None,
        driver_executable=None,
        settings=None,
    ):

        self.driver_executable = driver_executable
        self.driver = None
        self.user_dir = None

        super().__init__(
            request=request,
            url=url,
            settings=settings,
        )

    def set_settings(self, settings):
        from ..webconfig import WebConfig

        super().set_settings(settings)
        self.driver_executable = None

        if (
            settings
            and "settings" in settings
            and "driver_executable" in settings["settings"]
            and settings["settings"]["driver_executable"]
        ):
            self.driver_executable = settings["settings"]["driver_executable"]

        if self.driver_executable is None:
            self.driver_executable = WebConfig.default_chromedriver_path

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

    def after_load(self):
        """
        To be implemented by subordinate selenium crawlers
        """
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC

        if "settings" in self.settings and "delay_s" in self.settings["settings"]:
            delay_s = self.settings["settings"]["delay_s"]
            time.sleep(delay_s)

        REJECT_TEXTS = ["REJECT ALL", "Reject all", "Odrzuć", "Odrzuć wszystko"]

        if self.request.url.find("youtube.com/@"):
            # Try each reject button text
            for text in REJECT_TEXTS:
                try:
                    reject_button = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable(
                            (By.XPATH, f"//button[contains(text(), '{text}')]")
                        )
                    )
                    reject_button.click()
                    print(f"Clicked reject button with text: '{text}'")
                    break  # Exit the loop after successful click
                except Exception:
                    continue

    def run(self):
        """
        To obtain RSS page you have to run real, full blown browser.

        It may require some magic things to make the browser running.

        https://stackoverflow.com/questions/50642308/webdriverexception-unknown-error-devtoolsactiveport-file-doesnt-exist-while-t
        """
        if not self.is_valid():
            return

        self.response = PageResponseObject(
            self.request.url,
            text=None,
            status_code=HTTP_STATUS_CODE_SERVER_ERROR,
            request_url=self.request.url,
        )

        try:
            from selenium.common.exceptions import TimeoutException
        except Exception as E:
            self.response.add_error(str(E))
            print(str(E))
            selenium_feataure_enabled = False

        self.driver = self.get_driver()
        if not self.driver:
            return

        SeleniumDriver.counter += 1

        try:
            # add 10 seconds for start of browser, etc.
            selenium_timeout = self.get_timeout_s()

            self.driver.set_page_load_timeout(selenium_timeout)

            self.driver.get(self.request.url)

            self.after_load()

            self.process_response()

        except TimeoutException:
            error_text = traceback.format_exc()
            print("Page timeout:{}\n{}".format(self.request.url, error_text))
            WebLogger.debug(
                info_text="Page timeout:{}".format(self.request.url),
                detail_text=error_text,
            )
            self.response = PageResponseObject(
                self.request.url,
                text=None,
                status_code=HTTP_STATUS_CODE_TIMEOUT,
                request_url=self.request.url,
            )
            self.response.add_error("Url:{} Page timeout".format(self.request.url))

        except Exception as E:
            str_exc = str(E)
            if str_exc.find("net::ERR_NAME_NOT_RESOLVED") >= 0:
                WebLogger.debug("Url:{} connection error".format(self.request.url))
                self.response = PageResponseObject(
                    self.request.url,
                    text=None,
                    status_code=HTTP_STATUS_CODE_CONNECTION_ERROR,
                    request_url=self.request.url,
                )
                self.response.add_error(
                    "Url:{} Connection error".format(self.request.url)
                )
            elif str_exc.find("net::ERR_SSL_VERSION_OR_CIPHER_MISMATCH") >= 0:
                print(E, "Url:{}".format(self.request.url))
                WebLogger.exc(E, "Url:{}".format(self.request.url))
                self.response = PageResponseObject(
                    self.request.url,
                    text=None,
                    status_code=HTTP_STATUS_SSL_CERTIFICATE_ERROR,
                    request_url=self.request.url,
                )
                self.response.add_error("Url:{} ssl certificate error".format(self.request.url))
            else:
                print(E, "Url:{}".format(self.request.url))
                WebLogger.exc(E, "Url:{}".format(self.request.url))
                self.response = PageResponseObject(
                    self.request.url,
                    text=None,
                    status_code=HTTP_STATUS_CODE_EXCEPTION,
                    request_url=self.request.url,
                )
                self.response.add_error("Url:{} exception".format(self.request.url))

        return self.response

    def process_response(self):
        """
        TODO - if webpage changes link, it should also update it in this object
        """

        page_source = self.driver.page_source

        logs = self.driver.get_log("performance")
        info = self.read_logs(logs)

        headers = {}
        status_code = 200

        if "status_code" in info:
            status_code = info["status_code"]
        if "headers" in info:
            headers = info["headers"]

        self.response = PageResponseObject(
            self.driver.current_url,
            text=page_source,
            status_code=status_code,
            headers=headers,
            request_url=self.request.url,
        )

        if len(info) == 0:
            self.response.add_error("Cannot read driver logs")

    def read_logs(self, logs):
        info = {}
        try:
            info["status_code"] = self.get_selenium_status_code_from_logs(logs)
            info["headers"] = self.get_selenium_headers_from_logs(logs)
        except Exception as E:
            print(str(E))
        return info

    def get_response_logs(self, logs):
        # Parse the Chrome Performance logs
        response = None
        for log_entry in logs:
            log_message = json.loads(log_entry["message"])["message"]
            # Filter out HTTP responses
            if log_message["method"] == "Network.responseReceived":
                # self.responses.append(log_message["params"]["response"])
                if log_message["params"]["type"] == "Document":
                    return log_message["params"]["response"]

    def get_selenium_status_code_from_logs(self, logs):
        """
        Extracts the last HTTP status code for a specific URL from Selenium performance logs.
        """
        response = self.get_response_logs(logs)
        if response:
            return response["status"]
        else:
            return 0

    def get_selenium_headers_from_logs(self, logs):
        """
        Extracts the last HTTP status code for a specific URL from Selenium performance logs.
        """
        response = self.get_response_logs(logs)
        if response:
            return response["headers"]

    def close(self):
        from ..webconfig import WebConfig

        """
        https://stackoverflow.com/questions/15067107/difference-between-webdriver-dispose-close-and-quit
        """
        closed = False

        try:
            if self.driver:
                closed = True
                self.driver.close()
        except Exception as E:
            WebLogger.error(str(E))  # TODO
            WebLogger.debug(str(E))

        if not closed:
            return

        if SeleniumDriver.counter > 0:
            SeleniumDriver.counter -= 1

        WebLogger.debug("Selenium drivers count:{} ".format(SeleniumDriver.counter))
        time.sleep(1)

        if SeleniumDriver.counter == 0:
            if WebConfig.count_chrom_processes() == 0:
                return

            try:
                if self.driver:
                    self.driver.quit()
            except Exception as E:
                WebLogger.error(str(E))  # TODO
                WebLogger.debug(str(E))

            time.sleep(1)
            WebConfig.kill_chrom_processes()
            WebConfig.kill_xvfb_processes()

        if self.user_dir:
            try:
                shutil.rmtree(self.user_dir, ignore_errors=True)
            except Exception as E:
                WebLogger.error(str(E))  # TODO
                WebLogger.debug(str(E))

            self.user_dir = None


class SeleniumChromeHeadless(SeleniumDriver):
    """
    Selenium chrome headless
    """

    def get_driver(self):
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

            from selenium.webdriver.common.proxy import Proxy, ProxyType

        capabilities = webdriver.DesiredCapabilities.CHROME.copy()

        # Proxy Configuration
        if any(
            key in self.settings for key in ["http_proxy", "socks_proxy", "ssl_proxy"]
        ):
            prox = Proxy()
            prox.proxy_type = ProxyType.MANUAL
            prox.http_proxy = self.settings.get("http_proxy")
            prox.socks_proxy = self.settings.get("socks_proxy")
            prox.ssl_proxy = self.settings.get("ssl_proxy")
            prox.add_to_capabilities(capabilities)

        # Validate Chromedriver Executable
        if self.driver_executable:
            p = Path(self.driver_executable)
            if not p.exists():
                WebLogger.error(
                    f"Chromedriver executable not found at: {self.driver_executable}"
                )
                return None
            service = Service(executable_path=self.driver_executable)
        else:
            service = Service()

        # Chrome Options
        options = webdriver.ChromeOptions()
        options.add_argument("--headless=new")
        options.add_argument("--lang=en-US")

        # sometimes two selenium browser clash when accessing user data directory
        self.user_dir = tempfile.mkdtemp()
        print(f"using data dir {self.user_dir}")
        options.add_argument(f"--user-data-dir={self.user_dir}")

        # options to enable performance log, to read status code
        options.set_capability("goog:loggingPrefs", {"performance": "ALL"})

        # Add Proxy Capabilities
        for key, value in capabilities.items():
            options.set_capability(key, value)

        # Initialize WebDriver
        try:
            driver = webdriver.Chrome(service=service, options=options)
            return driver
        except Exception as E:
            WebLogger.error(f"Failed to initialize WebDriver: {E} Driver location:{self.driver_executable}")
            self.response.add_error(str(E))
            return None

    def is_valid(self):
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

        return selenium_feataure_enabled


class SeleniumChromeFull(SeleniumDriver):
    """
    Selenium chrome full - TODO
    """

    def get_driver(self):
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
        from selenium.webdriver.common.proxy import Proxy, ProxyType

        # capabilities = webdriver.DesiredCapabilities.CHROME.copy()

        # Proxy Configuration
        if self.settings and any(
            key in self.settings for key in ["http_proxy", "socks_proxy", "ssl_proxy"]
        ):
            prox = Proxy()
            prox.proxy_type = ProxyType.MANUAL
            prox.http_proxy = self.settings.get("http_proxy")
            prox.socks_proxy = self.settings.get("socks_proxy")
            prox.ssl_proxy = self.settings.get("ssl_proxy")
            # prox.add_to_capabilities(capabilities)

        # capabilities["goog:loggingPrefs"] = {"performance": "ALL"}
        # capabilities["loggingPrefs"] = {"performance": "ALL"}

        # Validate Chromedriver Executable
        if self.driver_executable:
            p = Path(self.driver_executable)
            if not p.exists():
                WebLogger.error(
                    f"Chromedriver executable not found at: {self.driver_executable}"
                )
                return None
            service = Service(executable_path=self.driver_executable)
        else:
            service = Service()

        options = webdriver.ChromeOptions()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--lang={}".format("en-US"))

        # path = "./linklibrary/rsshistory/static/extensions/chrome/ublock_1.61.2_0.crx"
        # options.add_extension(path)

        # Add Proxy Capabilities
        # for key, value in capabilities.items():
        #    options.set_capability(key, value)

        options.add_argument("start-maximized")
        options.add_argument("disable-infobars")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-gpu")

        # sometimes two selenium browser clash when accessing user data directory
        self.user_dir = tempfile.mkdtemp()
        print(f"Using user data dir {self.user_dir}")
        options.add_argument(f"--user-data-dir={self.user_dir}")

        # options to enable performance log, to read status code
        options.set_capability("goog:loggingPrefs", {"performance": "ALL"})

        # Initialize WebDriver
        try:
            driver = webdriver.Chrome(service=service, options=options)
            return driver
        except Exception as e:
            e_str = str(e)
            if e_str.find("session not created: probably user data directory is already in use, please specify a unique value for") >= 0:
                self.response = PageResponseObject(
                    self.request.url,
                    text=None,
                    status_code=HTTP_STATUS_CODE_SERVER_ERROR,
                    request_url=self.request.url,
                )
            elif e_str.find("Unable to obtain driver for chrome") >= 0:
                self.response = PageResponseObject(
                    self.request.url,
                    text=None,
                    status_code=HTTP_STATUS_CODE_SERVER_ERROR,
                    request_url=self.request.url,
                )
            else:
                self.response = PageResponseObject(
                    self.request.url,
                    text=None,
                    status_code=HTTP_STATUS_CODE_CONNECTION_ERROR,
                    request_url=self.request.url,
                )

            WebLogger.error(f"Failed to initialize WebDriver: {e} Driver location:{self.driver_executable}")
            return None

    def is_valid(self):
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
        return selenium_feataure_enabled

    def close(self):
        super().close()


class SeleniumUndetected(SeleniumDriver):
    """
    Selenium undetected
    """

    def get_driver(self):
        """
        NOTE: This driver may not work on raspberry PI
        """
        from selenium.webdriver.common.proxy import Proxy, ProxyType
        import undetected_chromedriver as uc

        options = uc.ChromeOptions()

        # Proxy Configuration
        if any(
            key in self.settings for key in ["http_proxy", "socks_proxy", "ssl_proxy"]
        ):
            prox = Proxy()
            prox.proxy_type = ProxyType.MANUAL
            prox.http_proxy = self.settings.get("http_proxy")
            prox.socks_proxy = self.settings.get("socks_proxy")
            prox.ssl_proxy = self.settings.get("ssl_proxy")
            prox.add_to_capabilities(options.experimental_options)

        options.set_capability("goog:loggingPrefs", {"performance": "ALL"})
        options.add_argument("--lang={}".format("en-US"))

        # sometimes two selenium browser clash when accessing user data directory
        self.user_dir = tempfile.mkdtemp()
        options.add_argument(f"--user-data-dir={self.user_dir}")

        try:
            return uc.Chrome(options=options)
        except Exception as E:
            error_text = traceback.format_exc()
            WebLogger.debug(
                "Cannot obtain driver:{}\n{}".format(self.request.url, error_text)
            )
            return

    def is_valid(self):
        try:
            import undetected_chromedriver as uc

            return True
        except Exception as E:
            return False


class SeleniumWireFull(SeleniumDriver):

    def get_driver(self):
        selenium_feature_enabled = True
        try:
            from selenium.webdriver.chrome.service import Service
            from selenium.common.exceptions import TimeoutException
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
        except Exception as E:
            print(str(E))
            selenium_feature_enabled = False

        from seleniumwire import webdriver as wire_webdriver
        from selenium.webdriver.common.proxy import Proxy, ProxyType

        seleniumwire_options = {}
        proxy_enabled = self.settings and any(
            key in self.settings for key in ["http_proxy", "socks_proxy", "ssl_proxy"]
        )

        if proxy_enabled:
            proxy_str = (
                self.settings.get("http_proxy")
                or self.settings.get("socks_proxy")
                or self.settings.get("ssl_proxy")
            )
            seleniumwire_options["proxy"] = {
                "http": proxy_str,
                "https": proxy_str,
                "no_proxy": "localhost,127.0.0.1",  # Optional
            }

        # Validate Chromedriver Executable
        if self.driver_executable:
            p = Path(self.driver_executable)
            if not p.exists():
                print(f"Chromedriver executable not found at: {self.driver_executable}")
                WebLogger.error(
                    f"Chromedriver executable not found at: {self.driver_executable}"
                )
                return None
            service = Service(executable_path=self.driver_executable)
        else:
            service = Service()

        options = wire_webdriver.ChromeOptions()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--lang=en-US")
        options.add_argument("start-maximized")
        options.add_argument("disable-infobars")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-gpu")

        # sometimes two selenium browser clash when accessing user data directory
        temp_user_data_dir = tempfile.mkdtemp()
        options.add_argument(f"--user-data-dir={temp_user_data_dir}")

        options.set_capability("goog:loggingPrefs", {"performance": "ALL"})

        try:
            driver = wire_webdriver.Chrome(
                service=service,
                options=options,
                seleniumwire_options=seleniumwire_options,
            )
            return driver
        except Exception as e:
            WebLogger.error(f"Failed to initialize WebDriver: {e}")
            print(f"Failed to initialize WebDriver: {e} Driver location:{self.driver_executable}")
            return None

    def process_response(self):
        last_status_code = 200
        last_headers = {}

        for request in self.driver.requests:
            if request.response:
                last_status_code = request.response.status_code
                last_headers = dict(request.response.headers)

        page_source = self.driver.page_source

        self.response = PageResponseObject(
            self.driver.current_url,
            text=page_source,
            status_code=last_status_code,
            headers=last_headers,
            request_url=self.request.url,
        )

    def is_valid(self):
        try:
            from seleniumwire import webdriver as wire_webdriver
            from selenium.webdriver.common.proxy import Proxy, ProxyType
            from seleniumwire import webdriver as wire_webdriver
        except Exception as E:
            return False

        return True


class ScriptCrawler(CrawlerInterface):
    """
    Used to run script to obtain URL response.
    Calls script, and receives reply in the file.

    Note:
     If we have multiple instances/workspaces each can write their own output file
    """

    def __init__(
        self,
        request=None,
        url=None,
        cwd=None,
        script=None,
        settings=None,
    ):
        super().__init__(
            request=request,
            url=url,
            settings=settings,
        )
        self.cwd = cwd
        self.script = script

    def set_response_file(self):
        if "response_file" in self.settings["settings"]:
            self.response_file = self.settings["settings"]["response_file"]

        if not self.response_file:
            from ..webconfig import WebConfig

            if WebConfig.script_responses_directory is not None:
                response_dir = Path(WebConfig.script_responses_directory)
            else:
                response_dir = Path("storage")

            self.response_file = (
                self.get_main_path() / response_dir / self.get_response_file_name()
            )

    def set_settings(self, settings):
        super().set_settings(settings)

        self.set_response_file()

        inner = self.settings["settings"]

        if inner and "script" in inner and inner["script"]:
            self.script = inner["script"]

        if inner and "cwd" in inner:
            self.cwd = inner["cwd"]

        if not self.cwd:
            self.cwd = self.get_main_path()

        if inner and "remote_server" in inner:
            return

    def run(self):
        if not self.is_valid():
            return

        inner = self.settings["settings"]

        if inner and "remote_server" in inner:
            return self.run_via_server(inner["remote_server"])
        else:
            return self.run_via_file()

    def run_via_server(self, remote_server):
        self.response = PageResponseObject(
            self.request.url,
            text=None,
            status_code=HTTP_STATUS_CODE_SERVER_ERROR,
            request_url=self.request.url,
        )

        script = self.script + ' --url "{}" --remote-server="{}" --timeout={}'.format(
            self.request.url, remote_server, self.get_timeout_s()
        )

        # WebLogger.error("Response:{}".format(self.response_file))
        # WebLogger.error("CWD:{}".format(self.cwd))
        # WebLogger.error("maintl:{}".format(self.get_main_path()))
        # WebLogger.error("script:{}".format(script))

        print("Running CWD:{} script:{}".format(self.cwd, script))

        try:
            p = subprocess.run(
                script,
                shell=True,
                capture_output=True,
                cwd=self.cwd,
                timeout=self.get_timeout_s() + 5,  # add more time for closing browser, etc
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

        import requests
        from ..remoteserver import RemoteServer

        url = f"{remote_server}/findj?url={self.request.url}"
        response = requests.get(url)

        if response.status_code == 200:
            try:
                data = response.json()

                server = RemoteServer("")
                self.response = server.get_response(data)

                return self.response

            except ValueError as E:
                print("Response content is not valid JSON. {}".format(E))
        else:
            WebLogger.error(
                f"Url:{self.request.url}: Failed to fetch data. Status code: {response.status_code}"
            )

            self.response = PageResponseObject(
                self.request.url,
                text=None,
                status_code=HTTP_STATUS_CODE_SERVER_ERROR,
                request_url=self.request.url,
            )

    def run_via_file(self):
        self.response = PageResponseObject(
            self.request.url,
            text=None,
            status_code=HTTP_STATUS_CODE_SERVER_ERROR,
            request_url=self.request.url,
        )

        response_file_location = Path(self.response_file)
        print("Running via file {}".format(response_file_location))

        if len(response_file_location.parents) > 1:
            response_dir = response_file_location.parents[1]
            if not response_dir.exists():
                response_dir.mkdir(parents=True, exist_ok=True)

        file_abs = response_file_location
        if file_abs.exists():
            file_abs.unlink()

        script = self.script + ' --url "{}" --output-file="{}" --timeout={}'.format(
            self.request.url, self.response_file, self.get_timeout_s()
        )

        # WebLogger.error("Response:{}".format(self.response_file))
        # WebLogger.error("CWD:{}".format(self.cwd))
        # WebLogger.error("maintl:{}".format(self.get_main_path()))
        # WebLogger.error("script:{}".format(script))
        print("Running script:{}".format(script))

        try:
            p = subprocess.run(
                script,
                shell=True,
                capture_output=True,
                cwd=self.cwd,
                timeout=self.get_timeout_s() + 10,  # add more time for closing browser, etc
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
        from ..webconfig import WebConfig

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


class SeleniumBase(CrawlerInterface):
    """
    Missing many things
    """

    def __init__(
        self,
        request,
        driver_executable=None,
        settings=None,
    ):
        super().__init__(
            request=request,
            settings=settings,
        )

    def run(self):
        if not self.is_valid():
            return

        self.response = PageResponseObject(
            self.request.url,
            text=None,
            status_code=HTTP_STATUS_CODE_SERVER_ERROR,
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
