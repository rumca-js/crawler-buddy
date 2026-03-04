"""
Provides default web configuratoin
"""

import os
import psutil
from pathlib import Path

from urllib3.exceptions import InsecureRequestWarning
from urllib3 import disable_warnings

from webtoolkit import (
    RequestsCrawler,
    PageRequestObject,
    WebLogger,
)

from .crawlers import (
    SeleniumChromeHeadless,
    SeleniumChromeFull,
    SeleniumUndetected,
    ScriptCrawler,
    SeleniumBase,
    SeleniumWireFull,
    StealthRequestsCrawler,
    CurlCffiCrawler,
    HttpxCrawler,
    YtdlpCrawler,
    HttpMorphCrawler,
    HttpCloakCrawler,
)


class CrawleeBeautifulScript(ScriptCrawler):
    def __init__(self, url=None,request=None):
        super().__init__(url=url,
                         request=request,
                         script=WebConfig.get_script_path("crawleebeautifulsoup.py"))


class CrawleePlaywrightScript(ScriptCrawler):
    def __init__(self, url=None, request=None):
        super().__init__(url=url,
                         request=request,
                         script=WebConfig.get_script_path("crawleeplaywright.py"))


class ScrapyScript(ScriptCrawler):
    def __init__(self, url=None, request=None):
        super().__init__(url=url,
                         request=request,
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

    def get_default_crawler_name():
        return "CurlCffiCrawler"

    def get_crawlers_raw():
        """
        Returns crawler classes
        """
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
            YtdlpCrawler,
            HttpMorphCrawler,
            HttpCloakCrawler,
        ]

        return crawlers

    def get_init_crawler_config():
        """
        Return crawlers configuration
        """
        mapping = []

        """
        mapping.append(WebConfig.get_default_browser_setup(RequestsCrawler))

        mapping.append(WebConfig.get_default_browser_setup(StealthRequestsCrawler))
        mapping.append(WebConfig.get_default_browser_setup(CurlCffiCrawler))
        mapping.append(WebConfig.get_default_browser_setup(HttpxCrawler))
        mapping.append(WebConfig.get_default_browser_setup(HttpMorphCrawler))
        mapping.append(WebConfig.get_default_browser_setup(HttpCloakCrawler))

        mapping.append(WebConfig.get_seleniumundetected())
        mapping.append(WebConfig.get_seleniumheadless())
        mapping.append(WebConfig.get_seleniumfull())
        mapping.append(WebConfig.get_seleniumbase())

        mapping.append(WebConfig.get_default_browser_setup(CrawleeBeautifulScript))
        mapping.append(WebConfig.get_default_browser_setup(CrawleePlaywrightScript))
        mapping.append(WebConfig.get_default_browser_setup(ScrapyScript))

        mapping.append(WebConfig.get_default_browser_setup(SeleniumWireFull, timeout_s=50))
        """
        mapping.append(WebConfig.get_scriped_crawler("RequestsCrawler"))
        mapping.append(WebConfig.get_scriped_crawler("CurlCffiCrawler"))
        mapping.append(WebConfig.get_scriped_crawler("HttpMorphCrawler"))
        mapping.append(WebConfig.get_scriped_crawler("SeleniumChromeFull"))
        mapping.append(WebConfig.get_default_browser_setup(YtdlpCrawler))

        return mapping

    def get_default_timeout_s():
        return 300

    def get_scriped_crawler(name):
        return {
            "crawler_name": name,
            "crawler_class" : ScriptCrawler,
            "settings": {
            },
        }

    def get_crawler_names():
        """
        Returns string representation
        """
        str_crawlers = []
        for mapping_data in WebConfig.get_init_crawler_config():
            str_crawlers.append(mapping_data["crawler_name"])

        return str_crawlers

    def get_crawler_from_string(crawler_string):
        """
        Returns crawler for input string
        """
        if not crawler_string:
            return

        init_mapping_data = WebConfig.get_init_crawler_config()
        for mapping_data in init_mapping_data:
            if mapping_data["crawler_name"] == crawler_string:
                return mapping_data["crawler_class"]

    def get_crawler_from_mapping(request, mapping_data):
        crawler_class = None

        if "crawler" in mapping_data and mapping_data["crawler"]:
            crawler_class = mapping_data["crawler"]

        if "crawler_name" in mapping_data and mapping_data["crawler_name"]:
            crawler_class = WebConfig.get_crawler_from_string(mapping_data["crawler_name"])

        if "crawler_class" in mapping_data and mapping_data["crawler_class"]:
            crawler_class = mapping_data["crawler_class"]

        if crawler_class is None and request:
            crawler_class = WebConfig.get_crawler_from_string(request.crawler_type)

        if not crawler_class:
            return

        settings = mapping_data["settings"]

        c = crawler_class(request=request, settings=settings)
        if c.is_valid():
            return c

    def get_crawlers():
        result = []
        mapping = WebConfig.get_init_crawler_config()
        for crawler in mapping:
            result.append(crawler)

        return result

    def get_default_crawler(url):
        configured_crawlers = WebConfig.get_init_crawler_config()
        for crawler_data in configured_crawlers:
            if crawler_data["crawler_name"] == WebConfig.get_default_crawler_name():
                return crawler_data

    def get_script_from_name(name):
        script = "crawlercurlcffi.py"
        if name == "CurlCffiCrawler":
            script = "crawlercurlcffi.py"
        if name == "RequestsCrawler":
            script = "crawlerrequests.py"
        if name == "HttpMorphCrawler":
            script = "crawlerhttpmorph.py"
        if name == "StealthRequestsCrawler":
            script = "crawlerstealth.py"
        if name == "SeleniumChromeFull":
            script = "crawlerseleniumfull.py"

        return script

    def get_default_request(url):

        crawler_data = WebConfig.get_default_crawler(url)
        if crawler_data:
            request = PageRequestObject(url)

            name = crawler_data["crawler_name"]
            script = WebConfig.get_script_from_name(name)

            request.crawler_name = name
            crawler_class = WebConfig.get_crawler_from_string(request.crawler_name)
            crawler_class = ScriptCrawler
            request.crawler_type = crawler_class(url=url, script=script)
            request.settings["script"] = script
            request.settings["remote_server"] = "http://127.0.0.1:3000"
            return request

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

    def get_default_browser_setup(browser, timeout_s=30):
        return {
            "crawler_name": browser.__name__,
            "crawler_class": browser,
            "settings": {"timeout_s": timeout_s},
        }

    def get_requests():
        return {
            "crawler_name": "RequestsCrawler",
            "settings": {"timeout_s": 40},
        }

    def get_default_chromedriver_path():
        return Path("/usr/bin/chromedriver")

    def get_seleniumheadless():
        chromedriver_path = WebConfig.get_default_chromedriver_path()

        if chromedriver_path.exists():
            return {
                "crawler_name": "SeleniumChromeHeadless",
                "crawler_class" : SeleniumChromeHeadless,
                "settings": {
                    "driver_executable": str(chromedriver_path),
                    "timeout_s": 60,
                },
            }
        else:
            return {
                "crawler_name": "SeleniumChromeHeadless",
                "crawler_class" : SeleniumChromeHeadless,
                "settings": {"driver_executable": None, "timeout_s": 60},
            }

    def get_seleniumfull():
        chromedriver_path = WebConfig.get_default_chromedriver_path()

        if chromedriver_path.exists():
            return {
                "crawler_name": "SeleniumChromeFull",
                "crawler_class" : SeleniumChromeFull,
                "settings": {
                    "driver_executable": str(chromedriver_path),
                    "timeout_s": 40,
                },
            }
        else:
            return {
                "crawler_name": "SeleniumChromeFull",
                "settings": {"driver_executable": None, "timeout_s": 60},
            }

    def get_seleniumundetected():
        chromedriver_path = WebConfig.get_default_chromedriver_path()

        if chromedriver_path.exists():
            return {
                "crawler_name": "SeleniumUndetected",
                "crawler_class" : SeleniumChromeFull,
                "settings": {
                    "driver_executable": str(chromedriver_path),
                    "timeout_s": 60,
                },
            }
        else:
            return {
                "crawler_name": "SeleniumUndetected",
                "settings": {"driver_executable": None, "timeout_s": 60},
            }

    def get_seleniumbase():
        return {
            "crawler_name": "SeleniumBase",
            "crawler_class" : SeleniumBase,
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

