# Crawling server

The Crawling Server is an HTTP-based web crawler that delivers data in an easily accessible JSON format.

 - No need to rely on tools like yt-dlp or Beautiful Soup for extracting link metadata.
 - Metadata is standardized with consistent fields (e.g., title, description, date_published, etc.).
 - Eliminates the need for custom HTTP wrappers to access RSS pages, even for sites with poorly configured bot protection.
 - Automatically discovers RSS feed URLs for websites and YouTube channels in many cases.
 - Simplifies data handling—no more parsing RSS files; just consume JSON!
 - Offers a unified interface for all metadata.
 - Running a containerized docker environment helps isolate problems from the host operating system
 - All your crawling / scraping / rss clients could use one source, or you can split it up by hosting multiple servers
 - Encoding? What encoding? All responses are in UTF

<div align="center">
  <img alt="Meme" src="images/crawler_buddy.png" style="width:450px">
</div>

Main Available Endpoints:
 - GET / - Provides index page
 - GET /info - Displays information about available crawlers.
 - GET /infoj - Similar to /info, but explicitly returns the information, in JSON format.
 - GET /system - Information about system.
 - GET /history - Displays the crawl history.
 - GET /historyj - Displays the crawl history, in JSON format.
 - GET /debug - debug information

Endpoints:
 - GET /get - form for getj Endpoint.
 - GET /getj - Crawls a specified page. Returns JSON
 - GET /contents - form for contentsr Endpoint
 - GET /contentsr - Returns contents of URL, and status code as is
 - GET /feeds - form for finding feeds for the specified URL
 - GET /feedsj - feeds information JSON
 - GET /social - form for social information
 - GET /socialj - Provides social information about a specified URL, thumbs up, view counts.
 - GET /link - form for link information
 - GET /linkj - Provides link information - canonical links, etc.
 - GET /ping - form for checking page status, if it is up, or not
 - GET /pingj - JSON response for ping
 - GET /archivesj - Provides archives links (to web archive etc)
 - GET /rssify - form for RSS contents
 - GET /rssifyr - returns RSS data for link
 - GET /scanlinksj - Provides JSON data with links present in the page
 - GET /scandomainsj - Provides JSON data with domains present in the page

Operation Endpoints:

 - GET /queue - Displays information about the current queue.
 - GET /removej - removes history entry
 - GET /find - form for findj Endpoint.
 - GET /findj - Retrieves the last crawl information for a specified URL.
    - Query parameter: url (string).
    - Response: Returns JSON with the last crawl details.

## /getj request

The getj Entpoint request arguments

- url (string): The URL to crawl
- crawler_name (optional, string): The name of the crawler
- crawler_data (optional, dict): Additional data for the crawler
- handler-name (optional, string): The name of the handler
- timeout_s (optional, int): timeout
- delay_s (optional, int): delay after load of page, necessary for javascript
- ssl_verify (optional, bool): indicates whether SSL problems should lead to errors
- bytes_limit (optional, int): accepted length limit of response bytes
- accept_types (optional, string): accepted types, "all" by default
- User-Agent (optional, string): define user agent
- request_headers (optional, dict): define headers
- settings (dict)

settings is a dict, with settings:
 - driver_executable (string): string to driver executable. Useful for selenium
 - script (string): string informing which script should be used. Useful if ScriptCrawler is used

## /getj response

Fields:

 - Properties - general properties, like title, description, thumbnail, language, date\_published, feed\_url
 - Streams - some handlers provide more data streams than "Text" or "Binary". For youtube we collect also yt-dlp JSON output, or return dislike data
 - Response - commonly used response fields Provides Content-Type, Content-Length, status\_code, etc. Contains also request data
 - Headers - all response headers of page. Provides Content-Type, Content-Length, etc.
 - Entries - if the link contains subordinate elements, like RSS, this field is populated with their meta data

You can see the structure in [Example response file](https://raw.githubusercontent.com/rumca-js/crawler-buddy/refs/heads/main/example_response.json)

Some fields need to be decoded from JSON string:
 - hash
 - body hash
 - binary data

```
base64.b64decode(encoded_string)
```

Notes:
 - Since some things are ambiguous we try to be consistent. For example: server content-type can be upper, or lower-case. This software always uses one strategy
 - Some things might be just fixed by project. No Content-Type, but we detected it is text/html, then software provides it in response
 - To sum up: the strategy is to fix what can be fixed, to make consistent things that are not

# Speed results

Manual test iterates over available crawlers and checks what is their speed

```
RequestsCrawler:            1.2801945209503174
CurlCffiCrawler:            0.8332247734069824
HttpxCrawler:               5.192519187927246
StealthRequestsCrawler:     0.7852857112884521
crawleebeautifulsoup.py:    14.384637832641602
```

# Automated access

To use output programmatically RemoteServer and Url classes was provided.

Please refer to [webtoolkit](https://github.com/rumca-js/webtoolkit)

## Additional features

Question: What if someone wants to make two paralell crawling methods, to make crawling faster?

Answer: Not a problem, just call twice /getj Endpoint, with different crawling methods, and use the first received response

Question: Does it support proxy?

Answer: I have provided some initial work for proxy, for Selenium. I do not however use proxies at all, so I have not checked if the code "works". This is crawler software, not a scraper

# Installation

For enhanced safety and ease of use, it's recommended to use the provided Docker image, as specified in the docker-compose configuration. Running browsers like Selenium within a containerized environment helps isolate them from the host operating system, offering an added layer of security.

Docker image is available at: https://hub.docker.com/r/rozbujnik/crawler-buddy.

## Crawling methods

Please see init_browser_setup.json to know which crawling methods are supported.

For example available are:
 - RequestsCrawler - python [requests](https://github.com/psf/requests)
 - SeleniumUndetected - [selenium undetected](https://github.com/ultrafunkamsterdam/undetected-chromedriver)
 - SeleniumChromeHeadless - [selenium](https://github.com/SeleniumHQ/selenium) chrome headless
 - SeleniumChromeFull - [selenium](https://github.com/SeleniumHQ/selenium) full mode
 - CurlCffiCrawler - [curl-cffi](https://github.com/lexiforest/curl_cffi) crawler
 - HttpxCrawler - [httpx](https://github.com/projectdiscovery/httpx) crawler
 - StealthRequestsCrawler - [stealth requests](https://github.com/jpjacobpadilla/Stealth-Requests)
 - CrawleeScript - [crawlee](https://github.com/apify/crawlee-python) beautifulsoup
 - PlaywrightScript - [crawlee](https://github.com/apify/crawlee-python) playwright
 - ScrapyScript - [scrapy](https://github.com/scrapy/scrapy)
 - SeleniumBase - [SeleniumBase](https://github.com/seleniumbase/SeleniumBase) [disabled]

Partial unverified support:
 - botasaurus

These methods can be selected for each individual URL for crawling.

Crawling methods like /crawlj can be called with crawl settings, which commonly are:
 - crawler_name - name of the desired crawler
 - crawler_type - crawler class
 - handler_class - handler clas, useful if you want to read an URL using 'HttpPageHandler', as normal vanilla HTTP processing, as if read by a browser
 - timeout_s - timout for crawling

No need to select methods manually, as some methods are already predefined and used automatically! Just take a look at entry_rules.json file!

## Supported platforms

 - YouTube - RSS feed discovery, social media data
 - HackerNews - social media
 - GitHub - social media
 - Reddit - RSS feed discovery, social media data
 - HTML pages - RSS feed discovery for links

File support
 - RSS / atom files
 - OMPL files
 - HTML files

# Scripts

Repository contains various crawling scripts. All start with 'crawl' prefix.

They can be manually called to see if crawling method works at all.

This repository provides the following programs:
 - script\_server: An HTTP crawling server.

# Script server CLI

```
usage: script_server.py [-h] [-l HISTORY_LENGTH]

Remote server options

options:
  -h, --help            show this help message and exit
  -l HISTORY_LENGTH, --history-length HISTORY_LENGTH
                        Length of history
