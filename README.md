This repository provides the following programs:
 - script\_server: An HTTP crawling server.
 - yafr: An RSS feed reader
 - page\_props: A script for retrieving page properties.

# Scraping server

The Scraping Server is an HTTP-based web crawler. Provides easily accessible data in JSON format.

Available Endpoints:

 - GET / - Provides index page
 - GET /info - Displays information about available crawlers. Returns JSON with crawler properties.
 - GET /infoj - Similar to /info, but explicitly returns the information in JSON format.
 - GET /history - Displays the crawl history.
 - GET /run - Crawls a specified page. Accepts the following query parameters:
 -- url (string): The URL to crawl.
 -- name (string): The name of the crawler.
 -- crawler (string): The crawler type.
 -- crawler_data (string): Additional data for the crawler.
 -- Response: Returns JSON with crawl properties.
 - GET /find - Retrieves the last crawl information for a specified URL.
 -- Query parameter: url (string).
 -- Response: Returns JSON with the last crawl details.
 - GET /social Provides social and dynamic information about a specified URL.
 -- Query parameter: url (string).
 -- Response: Returns JSON with social data.
 - POST /set - Saves custom crawl results for a URL. Accepts a JSON payload with the following fields:
 -- request_url (string): The target URL.
 -- Contents (string): The page content.
 -- Headers (object): HTTP headers.
 -- status_code (integer): The HTTP status code.
 -- Response: Acknowledges successful storage.

```
usage: script_server.py [-h] [--port PORT] [-l HISTORY_LENGTH] [--host HOST]

Remote server options

options:
  -h, --help            show this help message and exit
  -l HISTORY_LENGTH, --history-length HISTORY_LENGTH
                        Length of history
  --host HOST           Host
```

# Scripts

Repository contains various crawling scripts. All start with 'crawl' prefix.

They can be manually called to see if crawling method works at all.

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

