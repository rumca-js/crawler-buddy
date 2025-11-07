"""
With this script you can compare solutions.

This should be treated with a grain of salt, since all of them are called through OS subprocess.
To make crawlers results more objective all are called that way

In my setup it was around:
 requests: 2.9 [s]
 beautiful soup: 4.1 [s]
 playwright: 10.42 [s]
 selenium: not installed / missing
 selenium undetected: 12.62 [s]

# TODO check if status code is valid for all
"""

import time
import subprocess
import importlib
from pathlib import Path

from webtoolkit import file_to_response
import src.webtools.crawlers
from src.webtools import Url


# change test webpage to see if other pages can be scraped using different scrapers
test_webpage = "https://google.com"


def print_bar():
    print("---------------------")


def call_process(input_script, url = None):
    start_time = time.time()

    print(f"Running script {input_script} {url}")

    path = Path("out.txt")
    if path.exists():
        path.unlink()

    if url == None:
        url = test_webpage

    timeout_s = 55

    subprocess.check_call(
        "poetry run python {} --url {} --output-file {} --timeout {}".format(
            input_script, url, "out.txt", timeout_s
        ),
        shell=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        timeout=timeout_s,
    )

    response = file_to_response("out.txt")

    execution_time = time.time() - start_time
    print(f"Time: {execution_time}")

    if not response:
        print("No respone")
    if response and response.is_invalid():
        print("Response is invalid")

    print_bar()

    return [input_script + " " + url, execution_time, response]


def call_crawler(name):
    print(f"Running crawler {name}")

    start_time = time.time()
    execution_time = None
    response = None

    crawler_class = getattr(src.webtools.crawlers, name)
    crawler = crawler_class(url=test_webpage)
    if not crawler.is_valid():
        print(f"Crawler is {name} disabled")
    else:
        response = crawler.run()
        crawler.close()

        execution_time = time.time() - start_time
        print(f"Time: {execution_time}")

        if not response:
            print("No respone")
        if response and response.is_invalid():
            print("Response is invalid")

    print_bar()

    return [name, execution_time, response]

def test_url(url):
    start_time = time.time()

    print(f"Url test: {url}")
    url = Url(url = url)
    response = url.get_response()
    if not response:
        print("No respone")
    if response and response.is_invalid():
        print("Response is invalid")

    feeds = url.get_feeds()
    if feeds:
        print("Feeds {}".format(len(feeds)))

    streams = url.get_streams()
    if streams:
        print("Streams {}".format(len(streams)))

    entries = url.get_entries()
    if entries:
        print("Entries {}".format(len(entries)))

    execution_time = time.time() - start_time
    print(f"Time: {execution_time}")

    properties = url.get_social_properties()
    print(properties)

    print_bar()


def call_requests():
    return call_process("crawlerrequests.py")


def call_crawleebeautiful():
    return call_process("crawleebeautifulsoup.py")


def call_crawleeplaywright():
    return call_process("crawleeplaywright.py")


def call_seleniumchromeheadless():
    return call_process("crawlerseleniumheadless.py")


def call_seleniumchromefull():
    return call_process("crawlerseleniumfull.py")


def call_seleniumchromeundetected():
    return call_process("crawlerseleniumundetected.py")


def call_seleniumbase():
    return call_process("crawlerseleniumbase.py")


def test_crawlers():
    call_crawler("RequestsCrawler")
    call_crawler("CurlCffiCrawler")
    call_crawler("HttpxCrawler")
    call_crawler("StealthRequestsCrawler")
    call_crawler("SeleniumChromeHeadless")
    call_crawler("SeleniumChromeFull")
    call_crawler("SeleniumUndetected")
    call_crawler("SeleniumWireFull")

    call_crawleebeautiful()
    # call_crawleeplaywright()


def test_crawl_script():
    call_process("crawl.py", "https://www.youtube.com/watch?v=9yanqmc01ck")
    call_process("crawl.py", "https://www.youtube.com/feeds/videos.xml?channel_id=UCXuqSBlHAE6Xw-yeJA0Tunw")
    call_process("crawl.py", "https://www.youtube.com/channel/UCXuqSBlHAE6Xw-yeJA0Tunw")
    call_process("crawl.py", "https://www.youtube.com/@LinusTechTips")


def test_urls():
    test_url(url = "https://www.youtube.com/watch?v=9yanqmc01ck")
    test_url(url = "https://www.youtube.com/feeds/videos.xml?channel_id=UCXuqSBlHAE6Xw-yeJA0Tunw")
    test_url(url = "https://www.youtube.com/channel/UCXuqSBlHAE6Xw-yeJA0Tunw")
    test_url(url = "https://www.youtube.com/@LinusTechTips")
    test_url(url = "https://www.google.com")
    test_url(url = "https://www.github.com/rumca-js/Internet-Places-Database")
    test_url(url = "https://www.reddit.com/r/wizardposting")


def main():
    test_crawlers()
    test_crawl_script()
    test_urls()

main()
