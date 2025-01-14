# yafr

Yet another feed reader

```
usage: yafr.py [-h] [--timeout TIMEOUT] [--port PORT] [-o OUTPUT_DIR] [--add ADD] [--bookmark] [--unbookmark] [-m]
               [--entry ENTRY] [--source SOURCE] [-r] [--force] [--stats] [--cleanup] [--follow FOLLOW]
               [--unfollow UNFOLLOW] [--unfollow-all] [--enable ENABLE] [--disable DISABLE] [--enable-all ENABLE_ALL]
               [--disable-all DISABLE_ALL] [--list-bookmarks] [--list-entries] [--list-sources] [--init-sources]
               [--page-details PAGE_DETAILS] [--search SEARCH] [-v] [--db DB]

RSS feed program.

optional arguments:
  -h, --help            show this help message and exit
  --timeout TIMEOUT     Timeout expressed in seconds
  --port PORT           Port, if using web scraping server
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

Page properties can be obtained via commandline by means of page\_props.py program.

```
usage: page_props.py [-h] [--timeout TIMEOUT] [--port PORT] [--url URL] [--remote-server REMOTE_SERVER] [-v]

Page properties

options:
  -h, --help            show this help message and exit
  --timeout TIMEOUT     Timeout expressed in seconds
  --port PORT           Port, if using web scraping server
  --url URL             Url to fetch
  --remote-server REMOTE_SERVER
                        Remote crawling server
  -v, --verbose         Verbose. For example: displays full contents
```

# Scraping server

```
usage: script_server.py [-h] [--port PORT] [-l HISTORY_LENGTH] [--host HOST]

Remote server options

options:
  -h, --help            show this help message and exit
  --port PORT           Port number to be used
  -l HISTORY_LENGTH, --history-length HISTORY_LENGTH
                        Length of history
  --host HOST           Host
```

# Crawling

Repository contains various crawling scripts. All start with 'crawl' prefix.

They can be used to scrape information about a site.
