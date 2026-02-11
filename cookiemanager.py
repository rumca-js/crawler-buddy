
"""
Starts selenium, allows to store, or read cookies

Most cases:
 - you would like to load cookies & save cookies to udpate them
 - you would like to --wait & reject banners, accept condition & save cookies
"""

import json
import argparse
import time
from pathlib import Path

from webtoolkit import UrlLocation, PageRequestObject
from src.webtools import WebConfig


def parse():
    parser = argparse.ArgumentParser(description="Data analyzer program")
    parser.add_argument("--url", help="Directory to be scanned")
    parser.add_argument(
        "--timeout", default=10, type=int, help="Timeout expressed in seconds"
    )
    parser.add_argument("--ping", default=False, help="Ping only")
    parser.add_argument("--headers", default=False, help="Fetch headers only")
    parser.add_argument("--remote-server", help="Remote server")
    parser.add_argument("--proxy-address", help="Proxy address")
    parser.add_argument("--ssl-verify", default=False, help="SSL verify")

    parser.add_argument("--wait", default=False, action="store_true", help="Waits for user 'close' command")
    parser.add_argument("--load-cookies", default=False, action="store_true", help="Tries to load cookies")
    parser.add_argument("--save-cookies", default=False, action="store_true", help="Tries to save cookies")

    return parser.parse_args()


def main():
    WebConfig.init()
    WebConfig.use_print_logging()

    args = parse()

    link = args.url

    location = UrlLocation(link)
    domain_only = location.get_domain_only()
    domain = location.get_domain()

    request = PageRequestObject(link)

    selenium_config = WebConfig.get_seleniumfull()
    driver = WebConfig.get_crawler_from_mapping(request, selenium_config)
    if driver is None:
        print("Driver is NONE")
        return

    driver.driver_executable = "/usr/bin/chromedriver"

    driver.driver = driver.get_driver()
    if not driver.driver:
        print("Selenium driver is NONE")
        return

    if not args.wait:
        driver.driver.set_page_load_timeout(40)

    cookies = []
    if args.load_cookies:
        driver.load_cookies(link)

    driver.goto_page(link)

    if args.wait:
        while True:
            command = input("> ").strip().lower()
            if command == "close":
                break

    if args.save_cookies:
        if link != domain:
            print("Error: Cannot save cookies for url different than domain")
        else:
            driver.save_cookies(link)
            driver.save_page_source(domain_only)

    driver.close()


main()
