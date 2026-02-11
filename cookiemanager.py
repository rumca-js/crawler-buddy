
"""
Starts selenium, allows to store, or read cookies

Most cases:
 - you would like to load cookies & save cookies to udpate them
 - you would like to --wait & reject banners, accept condition & save cookies
"""

import json
import argparse
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
    parser.add_argument("--load-cookies", default=False, action="store_true", help="Tries to apply cookies")
    parser.add_argument("--save-cookies", default=False, action="store_true", help="Tries to apply cookies")

    return parser.parse_args()


def save_cookies(domain, cookies):
    print(f"URL:{domain} Saving cookies")
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)

    file_path = data_dir / f"{domain}.json"

    with file_path.open("w", encoding="utf-8") as fh:
        json.dump(cookies, fh, indent=4)


def save_page_source(domain, page_source):
    print(f"URL:{domain} Saving page source")

    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)

    file_path = data_dir / f"{domain}.html"
    with file_path.open("w", encoding="utf-8") as fh:
        fh.write(page_source)


def read_cookies(domain):
    print(f"URL:{domain} Reading cookies")

    data_dir = Path("data")
    if not data_dir.exists():
        return []

    file_path = data_dir / f"{domain}.json"
    if not file_path.exists():
        return []

    with file_path.open("r", encoding="utf-8") as fh:
        cookies = json.load(fh)

    return cookies


def apply_cookies(domain, selenium_driver, cookies):
    print(f"URL:{domain} Applying cookies")

    for cookie in cookies:
        if "expiry" in cookie:
            cookie["expiry"] = int(cookie["expiry"])
        try:
            selenium_driver.add_cookie(cookie)
        except Exception as E:
            print(f"Skipping cookie {cookie.get('name')}: {E}")



def main():
    WebConfig.init()
    WebConfig.use_print_logging()

    args = parse()

    link = args.url

    location = UrlLocation(link)
    domain = location.get_domain_only()

    request = PageRequestObject(link)

    selenium_config = WebConfig.get_seleniumfull()
    driver = WebConfig.get_crawler_from_mapping(request, selenium_config)
    if driver is None:
        print("Driver is NONE")
        return

    driver.driver_executable = "/usr/bin/chromedriver"

    selenium_driver = driver.get_driver()
    if not selenium_driver:
        print("Selenium driver is NONE")
        return

    if not args.wait:
        selenium_driver.set_page_load_timeout(40)

    selenium_driver.get(link)

    cookies = []
    if args.load_cookies:
        cookies = read_cookies(domain)
        apply_cookies(domain, selenium_driver, cookies)

    selenium_driver.refresh()

    if args.wait:
        while True:
            command = input("> ").strip().lower()
            if command == "close":
                break

    if args.save_cookies:
        cookies = selenium_driver.get_cookies()
        save_cookies(domain, cookies)

    page_source = selenium_driver.page_source
    save_page_source(domain, page_source)

    selenium_driver.close()


main()
