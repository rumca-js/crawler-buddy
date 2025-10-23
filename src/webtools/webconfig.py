"""
TODO
these scripts will not work in case of multithreaded app
"""

import os
import psutil
from pathlib import Path

from urllib3.exceptions import InsecureRequestWarning
from urllib3 import disable_warnings

from webtoolkit import WebLogger

from .crawlers import (
    RequestsCrawler,
    SeleniumChromeHeadless,
    SeleniumChromeFull,
    SeleniumUndetected,
    ScriptCrawler,
    SeleniumBase,
    SeleniumWireFull,
    StealthRequestsCrawler,
    CurlCffiCrawler,
    HttpxCrawler,
)


class CrawleeBeautifulScript(ScriptCrawler):
    def __init__(self, request=None, settings=None):
        super().__init__(request=request,
                         settings=settings,
                         script=WebConfig.get_script_path("crawleebeautifulsoup.py"))


class CrawleePlaywrightScript(ScriptCrawler):
    def __init__(self, request=None, settings=None):
        super().__init__(request=request,
                         settings=settings,
                         script=WebConfig.get_script_path("crawleeplaywright.py"))


class ScrapyScript(ScriptCrawler):
    def __init__(self, request=None, settings=None):
        super().__init__(request=request,
                         settings=settings,
                         script=WebConfig.get_script_path("cralwerscrapy.py"))


class WebConfig(object):
    """
    API to configure webtools
    """

    script_operating_dir = None
    script_responses_directory = Path("storage")
    display = None
    browser_mapping = {}
    default_chromedriver_path = Path("/usr/bin/chromedriver")

    def init():
        pass

    def get_crawlers_raw():
        crawlers = [
            RequestsCrawler,
            SeleniumChromeHeadless,  # requires driver location
            SeleniumChromeFull,  # requires driver location
            SeleniumUndetected,  # requires driver location
            SeleniumBase,
            SeleniumWireFull,
            StealthRequestsCrawler,
            CurlCffiCrawler,
            HttpxCrawler,
            CrawleeBeautifulScript,
            CrawleePlaywrightScript,
            ScrapyScript,
        ]

        return crawlers

    def get_init_crawler_config(headless_script=None, full_script=None, port=None):
        """
        Caller may provide scripts
        """
        mapping = []

        mapping.append(WebConfig.get_default_browser_setup(RequestsCrawler))

        mapping.append(WebConfig.get_default_browser_setup(StealthRequestsCrawler))
        mapping.append(WebConfig.get_default_browser_setup(CurlCffiCrawler))
        mapping.append(WebConfig.get_default_browser_setup(HttpxCrawler))

        mapping.append(WebConfig.get_seleniumundetected())
        mapping.append(WebConfig.get_seleniumheadless())
        mapping.append(WebConfig.get_seleniumfull())
        mapping.append(WebConfig.get_seleniumbase())

        mapping.append(WebConfig.get_default_browser_setup(CrawleeBeautifulScript))
        mapping.append(WebConfig.get_default_browser_setup(CrawleePlaywrightScript))
        mapping.append(WebConfig.get_default_browser_setup(ScrapyScript))

        mapping.append(WebConfig.get_default_browser_setup(SeleniumWireFull, timeout_s=50))

        return mapping

    def get_default_browser_setup(browser, enabled=True, timeout_s=30):
        return {
            "enabled": enabled,
            "name": browser.__name__,
            "settings": {"timeout_s": timeout_s},
        }

    def get_requests():
        return {
            "enabled": True,
            "name": "RequestsCrawler",
            "settings": {"timeout_s": 40},
        }

    def get_seleniumheadless():
        chromedriver_path = Path("/usr/bin/chromedriver")

        if chromedriver_path.exists():
            return {
                "enabled": False,
                "name": "SeleniumChromeHeadless",
                "settings": {
                    "driver_executable": str(chromedriver_path),
                    "timeout_s": 60,
                },
            }
        else:
            return {
                "enabled": True,
                "name": "SeleniumChromeHeadless",
                "settings": {"driver_executable": None, "timeout_s": 60},
            }

    def get_seleniumfull():
        chromedriver_path = Path("/usr/bin/chromedriver")

        if chromedriver_path.exists():
            return {
                "enabled": False,
                "name": "SeleniumChromeFull",
                "settings": {
                    "driver_executable": str(chromedriver_path),
                    "timeout_s": 40,
                },
            }
        else:
            return {
                "enabled": False,
                "name": "SeleniumChromeFull",
                "settings": {"driver_executable": None, "timeout_s": 60},
            }

    def get_seleniumundetected():
        chromedriver_path = Path("/usr/bin/chromedriver")

        if chromedriver_path.exists():
            return {
                "enabled": False,
                "name": "SeleniumUndetected",
                "settings": {
                    "driver_executable": str(chromedriver_path),
                    "timeout_s": 60,
                },
            }
        else:
            return {
                "enabled": False,
                "name": "SeleniumUndetected",
                "settings": {"driver_executable": None, "timeout_s": 60},
            }

    def get_seleniumbase():
        return {
            "enabled": False,
            "name": "SeleniumBase",
            "settings": {},
        }

    def get_script_path(script_relative):
        """
        script_relative example crawleebeautifulsoup.py
        """
        import os

        poetry_path = ""
        if "POETRY_ENV" in os.environ:
            poetry_path = os.environ["POETRY_ENV"] + "/bin/"

        script_relative = poetry_path + "poetry run python {}".format(script_relative)

        return script_relative

    def get_crawler_names():
        """
        Returns string representation
        """
        str_crawlers = []
        for crawler in WebConfig.get_crawlers_raw():
            str_crawlers.append(crawler.__name__)

        return str_crawlers

    def get_crawler_from_string(crawler_string):
        """
        Returns crawler for input string
        """
        if not crawler_string:
            return

        crawlers = WebConfig.get_crawlers_raw()
        for crawler in crawlers:
            if crawler.__name__ == crawler_string:
                return crawler

    def get_crawler_from_mapping(request, mapping_data):
        crawler_class = None

        if "crawler" in mapping_data and mapping_data["crawler"]:
            crawler_class = mapping_data["crawler"]

        if "name" in mapping_data and mapping_data["name"]:
            crawler_class = WebConfig.get_crawler_from_string(mapping_data["name"])

        if crawler_class is None and request:
            crawler_class = WebConfig.get_crawler_from_string(request.crawler_type)

        if not crawler_class:
            return

        settings = mapping_data["settings"]

        c = crawler(request=request, settings=settings)
        if c.is_valid():
            return c

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
                    WebLogger.error(
                        f"Killed process: {proc.info['name']} (PID: {proc.info['pid']})"
                    )
            except (
                psutil.NoSuchProcess,
                psutil.AccessDenied,
                psutil.ZombieProcess,
            ) as e:
                WebLogger.error(
                    f"Could not kill process {proc.info.get('name', 'unknown')}: {e}"
                )

    def kill_xvfb_processes():
        """Kill all processes whose names start with 'chrom'."""
        for proc in psutil.process_iter(["pid", "name"]):
            try:
                if proc.info["name"] and proc.info["name"].lower().startswith("xvfb"):
                    proc.kill()  # Kill the process
                    WebLogger.error(
                        f"Killed process: {proc.info['name']} (PID: {proc.info['pid']})"
                    )
            except (
                psutil.NoSuchProcess,
                psutil.AccessDenied,
                psutil.ZombieProcess,
            ) as e:
                WebLogger.error(
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
