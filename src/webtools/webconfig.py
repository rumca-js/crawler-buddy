"""
TODO
these scripts will not work in case of multithreaded app
"""

import os
import psutil
from pathlib import Path

from urllib3.exceptions import InsecureRequestWarning
from urllib3 import disable_warnings

from .webtools import WebLogger

from .crawlers import (
    RequestsCrawler,
    SeleniumChromeHeadless,
    SeleniumChromeFull,
    SeleniumUndetected,
    ScriptCrawler,
    SeleniumBase,
    StealthRequestsCrawler,
)


class WebConfig(object):
    """
    API to configure webtools
    """

    script_operating_dir = None
    script_responses_directory = Path("storage")
    display = None
    browser_mapping = {}

    def init():
        pass

    def get_browsers_raw():
        browsers = [
            RequestsCrawler,
            SeleniumChromeHeadless,  # requires driver location
            SeleniumChromeFull,  # requires driver location
            SeleniumUndetected,  # requires driver location
            ScriptCrawler,  # requires script
            SeleniumBase,
            StealthRequestsCrawler,
        ]

        return browsers

    def get_browsers():
        str_browsers = []
        for browser in WebConfig.get_browsers_raw():
            str_browsers.append(browser.__name__)

        return str_browsers

    def get_crawler_from_string(input_string):
        """
        TODO - apply generic approach
        """
        browsers = WebConfig.get_browsers_raw()
        for browser in browsers:
            if browser.__name__ == input_string:
                return browser

    def get_crawler_from_mapping(request, mapping_data):
        crawler = mapping_data["crawler"]
        if not crawler:
            return

        settings = mapping_data["settings"]

        c = crawler(request=request, settings=settings)
        if c.is_valid():
            return c

    def get_init_crawler_config(headless_script=None, full_script=None, port=None):
        """
        Caller may provide scripts
        """
        mapping = []

        # one of the methods should be available
        from .ipc import DEFAULT_PORT, SocketConnection

        if not port:
            port = DEFAULT_PORT

            c = SocketConnection()
            if not c.connect(host=SocketConnection.gethostname(), port=port):
                port = None

            c.close()

        try:
            import os
            from crawlee.beautifulsoup_crawler import BeautifulSoupCrawler

            poetry_path = ""
            if "POETRY_ENV" in os.environ:
                poetry_path = os.environ["POETRY_ENV"] + "/bin/"

            if full_script is None:
                full_script = poetry_path + "poetry run python crawleebeautifulsoup.py"
            if headless_script is None:
                headless_script = (
                    poetry_path + "poetry run python crawleebeautifulsoup.py"
                )
        except:
            pass

        mapping.append(WebConfig.get_default_browser_setup(RequestsCrawler))

        mapping.append(WebConfig.get_scriptcralwer(headless_script, "CrawleeScript"))
        mapping.append(WebConfig.get_scriptcralwer(full_script, "PlaywrightScript"))
        mapping.append(WebConfig.get_seleniumundetected())
        mapping.append(WebConfig.get_seleniumbase())
        mapping.append(WebConfig.get_seleniumheadless())
        mapping.append(WebConfig.get_seleniumfull())

        mapping.append(WebConfig.get_default_browser_setup(StealthRequestsCrawler))

        return mapping

    def get_crawlers(only_enabled=False):
        result = []
        mapping = WebConfig.get_init_crawler_config()
        for crawler in mapping:
            if only_enabled and crawler["enabled"]:
                result.append(crawler)
            else:
                result.append(crawler)

        return result

    def get_default_crawler(url):
        config = WebConfig.get_init_crawler_config()
        if config:
            crawler_data = dict(config[0])
            if "crawler" in crawler_data:
                crawler_data["crawler"] = crawler_data["crawler"](url=url)
                return crawler_data

    def get_default_browser_setup(browser, enabled=True):
        return {
            "enabled": enabled,
            "name": browser.__name__,
            "crawler": browser,
            "settings": {"timeout_s": 20},
        }

    def get_requests():
        return {
            "enabled": True,
            "name": "RequestsCrawler",
            "crawler": RequestsCrawler,
            "settings": {"timeout_s": 20},
        }

    def get_scriptcralwer(script, name=""):
        if script:
            return {
                "enabled": True,
                "name": name,
                "crawler": ScriptCrawler,
                "settings": {"script": script, "timeout_s": 40},
            }
        else:
            return {
                "enabled": False,
                "name": name,
                "crawler": ScriptCrawler,
                "settings": {"script": script, "timeout_s": 40},
            }

    def get_seleniumheadless():
        chromedriver_path = Path("/usr/bin/chromedriver")

        if chromedriver_path.exists():
            return {
                "enabled": False,
                "name": "SeleniumChromeHeadless",
                "crawler": SeleniumChromeHeadless,
                "settings": {
                    "driver_executable": str(chromedriver_path),
                    "timeout_s": 30,
                },
            }
        else:
            return {
                "enabled": True,
                "name": "SeleniumChromeHeadless",
                "crawler": SeleniumChromeHeadless,
                "settings": {"driver_executable": None, "timeout_s": 40},
            }

    def get_seleniumfull():
        chromedriver_path = Path("/usr/bin/chromedriver")

        if chromedriver_path.exists():
            return {
                "enabled": False,
                "name": "SeleniumChromeFull",
                "crawler": SeleniumChromeFull,
                "settings": {
                    "driver_executable": str(chromedriver_path),
                    "timeout_s": 40,
                },
            }
        else:
            return {
                "enabled": False,
                "name": "SeleniumChromeFull",
                "crawler": SeleniumChromeFull,
                "settings": {"driver_executable": None, "timeout_s": 40},
            }

    def get_seleniumundetected():
        chromedriver_path = Path("/usr/bin/chromedriver")

        if chromedriver_path.exists():
            return {
                "enabled": False,
                "name": "SeleniumUndetected",
                "crawler": SeleniumUndetected,
                "settings": {
                    "driver_executable": str(chromedriver_path),
                    "timeout_s": 30,
                },
            }
        else:
            return {
                "enabled": False,
                "name": "SeleniumUndetected",
                "crawler": SeleniumUndetected,
                "settings": {"driver_executable": None, "timeout_s": 40},
            }

    def get_seleniumbase():
        return {
            "enabled": False,
            "name": "SeleniumBase",
            "crawler": SeleniumBase,
            "settings": {},
        }

    def use_logger(Logger):
        WebLogger.web_logger = Logger

    def use_print_logging():
        from utils.logger import PrintLogger

        WebLogger.web_logger = PrintLogger()

    def disable_ssl_warnings():
        disable_warnings(InsecureRequestWarning)

    def kill_chrom_processes():
        """Kill all processes whose names start with 'chrom'."""
        for proc in psutil.process_iter(["pid", "name"]):
            try:
                if proc.info["name"] and proc.info["name"].lower().startswith("chrom"):
                    proc.kill()  # Kill the process
                    webtools.WebLogger.error(
                        f"Killed process: {proc.info['name']} (PID: {proc.info['pid']})"
                    )
            except (
                psutil.NoSuchProcess,
                psutil.AccessDenied,
                psutil.ZombieProcess,
            ) as e:
                webtools.WebLogger.error(
                    f"Could not kill process {proc.info.get('name', 'unknown')}: {e}"
                )

    def count_chrom_processes():
        """Count the number of running processes whose names start with 'chrom'."""
        count = 0
        for proc in psutil.process_iter(["pid", "name"]):
            try:
                if proc.info["name"] and proc.info["name"].lower().startswith("chrom"):
                    count += 1
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue  # Skip processes we can't access
        return count

    def start_display():
        try:
            from pyvirtualdisplay import Display

            # Check if WebConfig.display is already initialized and active
            if (
                isinstance(getattr(WebConfig, "display", None), Display)
                and WebConfig.display.is_alive()
            ):
                return  # Do nothing if already initialized and active

            # Requires xvfb
            os.environ["DISPLAY"] = ":10.0"

            # Create and start the Display
            WebConfig.display = Display(visible=0, size=(800, 600))
            WebConfig.display.start()
        except Exception as E:
            WebLogger.error(f"Problems with creating display: {str(E)}")
            return

    def stop_display():
        try:
            WebConfig.display.stop()
            WebConfig.display = None
        except Exception as E:
            WebLogger.error(f"Problems with creating display")
            return

    def get_bytes_limit():
        return 5000000  # 5 MB. There are some RSS more than 1MB
