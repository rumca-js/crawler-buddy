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


# change test webpage to see if other pages can be scraped using different scrapers
test_webpage = "https://google.com"


def call_process(input_script):
    start_time = time.time()

    print(f"Running script {input_script}")
    path = Path("out.txt")
    if path.exists():
        path.unlink()

    subprocess.check_call(
        "poetry run python {} --url {} --output-file {} --timeout 55".format(
            input_script, test_webpage, "out.txt"
        ),
        shell=True,
        timeout=20,
    )

    response = file_to_response("out.txt")

    return [input_script, time.time() - start_time, response]


def call_crawler(name):
    print(f"Running crawler {name}")

    start_time = time.time()

    crawler_class = getattr(src.webtools.crawlers, name)
    crawler = crawler_class(url=test_webpage)
    if not crawler.is_valid():
        print(f"Crawler is {name} disabled")
        return [name, None, None]

    response = crawler.run()
    crawler.close()

    return [name, time.time() - start_time, response]


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


def main():
    times = []
    times.append(call_crawler("RequestsCrawler"))
    times.append(call_crawler("CurlCffiCrawler"))
    times.append(call_crawler("HttpxCrawler"))
    times.append(call_crawler("StealthRequestsCrawler"))
    times.append(call_crawler("SeleniumChromeHeadless"))
    times.append(call_crawler("SeleniumChromeFull"))
    times.append(call_crawler("SeleniumUndetected"))
    times.append(call_crawler("SeleniumWireFull"))

    times.append(call_crawleebeautiful())
    # times.append(call_crawleeplaywright())

    print("---------------------")

    for time_data in times:
        if not time_data:
            return

        name = time_data[0]
        time = time_data[1]
        response = time_data[2]

        if response and response.is_valid():
            print("{}:\t{}".format(name, time))

    print("--------ALL----------")

    for time_data in times:
        if not time_data:
            return

        name = time_data[0]
        time = time_data[1]
        response = time_data[2]

        print("{}:{}".format(name, time))
        if response:
            print(response)

main()
