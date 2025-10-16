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


# change test webpage to see if other pages can be scraped using different scrapers
test_webpage = "https://google.com"


def call_process(input_script):
    start_time = time.time()

    print(f"Running script {input_script}")

    subprocess.check_call(
        "poetry run python {} --url {} --output-file {} --timeout 55".format(
            input_script, test_webpage, "out.txt"
        ),
        shell=True,
        timeout=20,
    )

    return time.time() - start_time


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
    time_requests = call_requests()
    time_crawleebeautiful = call_crawleebeautiful()
    #time_crawleeplaywright = call_crawleeplaywright()
    time_seleniumchromeheadless = call_seleniumchromeheadless()
    time_seleniumchromefull = call_seleniumchromefull()
    #time_seleniumchromeundetected = call_seleniumchromeundetected()
    #time_seleniumbase = call_seleniumbase()

    print(f"Requests:{time_requests} [s]")
    #print(f"crawleebeautifulsoup:{time_crawleebeautiful} [s]")
    #print(f"crawleeplaywright:{time_crawleeplaywright} [s]")
    print(f"seleniumchromeheadless:{time_seleniumchromeheadless} [s]")
    print(f"seleniumchromefull:{time_seleniumchromefull} [s]")
    #print(f"seleniumchromeundetected:{time_seleniumchromeundetected} [s]")
    #print(f"seleniumbase:{time_seleniumbase} [s]")


main()
