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
 - GET /info - Displays information about available crawlers. Returns JSON with crawler properties.
 - GET /infoj - Similar to /info, but explicitly returns the information, in JSON format.

Endpoints:
 - GET /get - form for getj Endpoint.
 - GET /getj - Crawls a specified page. Accepts the following query parameters:
    - url (string): The URL to crawl.
    - name (optional, string): The name of the crawler.
    - crawler (optional, string): The crawler type.
    - crawler_data (optional, string): Additional data for the crawler.
    - Response: Returns JSON with crawl properties.
 - GET /feeds - Provides form for finding feeds for the specified URL
 - GET /feedsj - Provides feeds information
 - GET /socialj - Provides social and dynamic information about a specified URL.
    - Query parameter: url (string).
    - Response: Returns JSON with social data.
 - GET /link - Provides for link information
 - GET /linkj - Provides link information - canonical links, etc.
 - GET /rss link data as RSS stream
 - GET /proxy - Returns URL data as is, contents, status_code. Useful if you try to access page that is only accessible by selenium, or crawlee
    - Response: Passes contents of response, and status code as is

Operation Endpoints:
 - GET /history - Displays the crawl history.
 - GET /historyj - Displays the crawl history, in JSON format.
 - GET /queue - Displays information about the current queue.
 - GET /removej - removes history entry
 - GET /find - form for findj Endpoint.
 - GET /findj - Retrieves the last crawl information for a specified URL.
    - Query parameter: url (string).
    - Response: Returns JSON with the last crawl details.

## GET request

The getj Entpoint request arguments. Either one needs to be true: name, crawler, or crawler_data.

- url (string): The URL to crawl
- name (optional, string): The name of the crawler
- crawler (optional, string): The crawler type
- crawler_data (optional, dict): Additional data for the crawler

crawler_data is a dict, with settings:
 - name (optional, string)
 - crawler (optional, string)
 - settings (dict)

settings is a dict, with settings:
 - timeout_s (int) - the amount of time we wait for a page response
 - delay_s (int) - delay which should be used after visiting a page using crawler. Useful if it is needed to wait for javascript.
 - driver_executable (string) string to driver executable. Useful for selenium
 - script (string) string informing which script should be used. Useful if ScriptCrawler is used

## GET response JSON

Fields:

 - Properties - general properties, like title, description, thumbnail, language, date\_published, feed\_url
 - Text - text contents of page
 - Binary - binary contents of page
 - Response - commonly used response fields Provides Content-Type, Content-Length, status\_code, etc.
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

# How to use the response?

Sure that is quite simple.

For Python RemoteServer has been provided in remoteserver.py file. To obtain all properties it is enough to use the following code:

```
link = "https://google.com"
server = RemoteServer(server_address)
all_properties = server.get_getj(url=link)
```

## Additional features

Question: What if someone wants to make two paralell crawling methods, to make crawling faster?

Answer: Not a problem, just call twice /getj Endpoint, with different crawling methods, and use the first received response

Question: Does it support proxy?

Answer: I have provided some initial work for proxy, for Selenium. I do not however use proxies at all, so I have not checked if the code "works". This is crawler software, not a scraper

# Installation

For enhanced safety and ease of use, it's recommended to use the provided Docker image, as specified in the docker-compose configuration. Running browsers like Selenium within a containerized environment helps isolate them from the host operating system, offering an added layer of security.

Docker image is available at: https://hub.docker.com/repository/docker/rozbujnik/crawler-buddy.

## Crawling methods

Please see init_browser_setup.json to know which crawling methods are supported.

For example available are:
 - RequestsCrawler - python requests
 - CrawleeScript - crawlee beautifulsoup
 - PlaywrightScript - crawlee playwright
 - SeleniumUndetected - selenium undetected
 - SeleniumChromeHeadless - selenium chrome headless
 - SeleniumChromeFull - selenium full mode
 - StealthRequestsCrawler - stealth requests
 - SeleniumBase - selenium base [disabled]

These methods can be selected for each individual URL for crawling.

Crawling methods like /crawlj can be called with crawl settings, which commonly are:
 - name - name of the desired crawler
 - crawler - crawler class
 - handler_class - handler clas, useful if you want to read an URL using 'HttpPageHandler', as normal vanilla HTTP processing, as if read by a browser
 - timeout_s - timout for crawling

No need to select methods manually, as some methods are already predefined and used automatically! Just take a look at entry_rules.json file!

## Supported platforms

 - YouTube - RSS feed discovery, social media data
 - HackerNews - social media
 - GitHub - social media
 - Reddit - RSS feed discovery, social media data
 - 4chan - RSS feed discovery
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
 - yafr: An RSS feed reader
 - page\_props: A script for retrieving page properties.

# Script server CLI

```
usage: script_server.py [-h] [--port PORT] [-l HISTORY_LENGTH] [--host HOST]

Remote server options

options:
  -h, --help            show this help message and exit
  -l HISTORY_LENGTH, --history-length HISTORY_LENGTH
                        Length of history
  --host HOST           Host
```


# yafr

Yet another feed reader

```
usage: yafr.py [-h] [--timeout TIMEOUT] [-o OUTPUT_DIR] [--add ADD] [--bookmark] [--unbookmark] [-m]
               [--entry ENTRY] [--source SOURCE] [-r] [--force] [--stats] [--cleanup] [--follow FOLLOW]
               [--unfollow UNFOLLOW] [--unfollow-all] [--enable ENABLE] [--disable DISABLE] [--enable-all ENABLE_ALL]
               [--disable-all DISABLE_ALL] [--list-bookmarks] [--list-entries] [--list-sources] [--init-sources]
               [--page-details PAGE_DETAILS] [--search SEARCH] [-v] [--db DB]

RSS feed program.

optional arguments:
  -h, --help            show this help message and exit
  --timeout TIMEOUT     Timeout expressed in seconds
  -o OUTPUT_DIR, --output-dir OUTPUT_DIR
                        HTML output directory
  --add ADD             Adds entry with the specified URL
  --bookmark            bookmarks entry
  --unbookmark          unbookmarks entry
  --remote-server REMOTE_SERVER
  -m, --mark-read       Marks entries as read
  --entry ENTRY         Select entry by ID
  --source SOURCE       Select source by ID
  -r, --refresh-on-start
                        Refreshes links, fetches on start
  --force               Force refresh
  --stats               Show table stats
  --cleanup             Remove unreferenced items
  --follow FOLLOW       Follows specific source
  --unfollow UNFOLLOW   Unfollows specific source
  --unfollow-all        Unfollows all sources
  --enable ENABLE       Enables specific source
  --disable DISABLE     Disables specific source
  --enable-all ENABLE_ALL
                        Enables all sources
  --disable-all DISABLE_ALL
                        Disables all sources
  --list-bookmarks      Prints bookmarks to stdout
  --list-entries        Prints data to stdout
  --list-sources        Lists sources
  --init-sources        Initializes sources
  --page-details PAGE_DETAILS
                        Shows page details for specified URL
  --search SEARCH       Search entries. Example: --search "title=Elon"
  -v, --verbose         Verbose
  --db DB               SQLite database file name
```

## Alternative software

 - https://newsboat.org/index.html
 - https://github.com/guyfedwards/nom
 - https://github.com/iamaziz/TermFeed
 - https://feed2exec.readthedocs.io
 - https://github.com/kpman/newsroom

## Alternative software - GUI

 - https://github.com/FreshRSS/FreshRSS
 - https://github.com/yang991178/fluent-reader
 - https://github.com/samuelclay/NewsBlur
 - https://github.com/stringer-rss/stringer
 - https://github.com/hello-efficiency-inc/raven-reader
 - https://tt-rss.org/
 - https://github.com/nkanaev/yarr
 - ...and more...

## where to find feed urls

First, try [OpenRss](https://openrss.org/usage)

Then, you can try searching by Google, or other search engine.

You can also check existing awesome lists:

 - https://github.com/plenaryapp/awesome-rss-feeds
 - https://github.com/tuan3w/awesome-tech-rss
 - https://github.com/DongjunLee/awesome-feeds
 - https://github.com/foorilla/allainews_sources

Other places to find interesting blogs / places:

 - https://nownownow.com/
 - https://searchmysite.net/
 - https://downloads.marginalia.nu/
 - https://aboutideasnow.com/
 - https://neocities.org/

## Other things

 - https://github.com/AboutRSS/ALL-about-RSS
 - https://github.com/voidfiles/awesome-rss standards
 
find interesting page, and try to follow it. if page contains valid RSS link this software should be able to follow it

# Page properties

This program allows to display page properties.

```
usage: page_props.py [-h] [--timeout TIMEOUT] [--url URL] [--remote-server REMOTE_SERVER] [-v]

Page properties

options:
  -h, --help            show this help message and exit
  --timeout TIMEOUT     Timeout expressed in seconds
  --url URL             Url to fetch
  --remote-server REMOTE_SERVER
                        Remote crawling server
  -v, --verbose         Verbose. For example: displays full contents
```

