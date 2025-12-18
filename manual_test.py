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
import webtoolkit
import src.webtools.crawlers
from src.webtools import Url
from src.webtools.webconfig import WebConfig


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


def call_crawler(test_link, name):
    print(f"Running {test_link} with {name} crawler")

    start_time = time.time()
    execution_time = None
    response = None

    crawler_class = WebConfig.get_crawler_from_string(name)
    crawler = crawler_class(url=test_link)
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
        if response and response.is_valid():
            print("Response is valid")

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

    if url.get_title() is None:
        print("Title is None!")

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


def test_crawlers():
    call_crawler(test_webpage, "RequestsCrawler")
    call_crawler(test_webpage, "CurlCffiCrawler")
    call_crawler("https://www.youtube.com/@LinusTechTips", "CurlCffiCrawler")
    call_crawler(test_webpage, "HttpxCrawler")
    call_crawler(test_webpage, "HttpMorphCrawler")
    call_crawler(test_webpage, "StealthRequestsCrawler")
    call_crawler(test_webpage, "SeleniumChromeHeadless")
    call_crawler(test_webpage, "SeleniumChromeFull")
    call_crawler(test_webpage, "SeleniumUndetected")
    call_crawler(test_webpage, "SeleniumWireFull")

    call_process("crawleebeautifulsoup.py")
    # call_crawleeplaywright()


def test_crawl_script():
    print("-----------")
    print("Testing how scripts exchange request/response data")
    print("-----------")
    call_process("crawl.py", "https://www.youtube.com/watch?v=9yanqmc01ck")
    call_process("crawl.py", "https://www.youtube.com/feeds/videos.xml?channel_id=UCXuqSBlHAE6Xw-yeJA0Tunw")
    call_process("crawl.py", "https://www.youtube.com/channel/UCXuqSBlHAE6Xw-yeJA0Tunw")
    call_process("crawl.py", "https://www.youtube.com/@LinusTechTips")


def test_urls():
    test_url(url = "https://www.google.com")
    test_url(url = "https://www.youtube.com/watch?v=9yanqmc01ck")
    test_url(url = "https://www.youtube.com/feeds/videos.xml?channel_id=UCXuqSBlHAE6Xw-yeJA0Tunw")
    test_url(url = "https://www.youtube.com/channel/UCXuqSBlHAE6Xw-yeJA0Tunw")
    test_url(url = "https://www.youtube.com/@LinusTechTips")
    test_url(url = "https://www.github.com/rumca-js/Internet-Places-Database")
    test_url(url = "https://www.reddit.com/r/wizardposting")
    test_url(url = "https://www.reddit.com/r/wizardposting/comments/1olomjs/screw_human_skeletons_im_gonna_get_more_creative/")

    #import httpmorph
    #response =  httpmorph.get("https://www.youtube.com/channel/UCXuqSBlHAE6Xw-yeJA0Tunw", timeout=30)
    #print(reponse.status_code)


def main():
    WebConfig.use_print_logging()
    webtoolkit.WebConfig.use_print_logging()

    test_crawlers()
    test_urls()
    test_crawl_script()

main()


#import time
#from src.taskrunner import start_runner_thread
#from src.crawlercontainer import CrawlerContainer
#
#container = CrawlerContainer()
#container.crawl(crawl_type=CrawlerContainer.CRAWL_TYPE_GET, url="https://google.com")
#container.crawl(crawl_type=CrawlerContainer.CRAWL_TYPE_GET, url="https://youtube.com")
#thread, runner = start_runner_thread(container)
#
#while(True):
#    if runner.is_empty():
#        print("Finished all")
#        runner.stop()
#        thread.join()
#        for item in container.container:
#            print(item)
#        break
#    time.sleep(1)
