"""
Starts server at the specified location

Access through:
    ip:port/getj?url=.... etc.
"""

from pathlib import Path
from flask import Flask, request, jsonify, Response
import socket
import json
import html
import subprocess
import base64
import traceback
from datetime import datetime

import webtoolkit
from webtoolkit import (
   HttpPageHandler,
   WebLogger,
   RemoteUrl,
   RemoteServer,
   PageRequestObject,
   PageResponseObject,
   ContentLinkParser,
   HTTP_STATUS_CODE_CONNECTION_ERROR,
   HTTP_STATUS_CODE_EXCEPTION,
   HTTP_STATUS_CODE_SERVER_TOO_MANY_REQUESTS,
)
from utils import PermanentLogger
from utils.systemmonitoring import get_hardware_info, get_process_info

from src import webtools
from src.configuration import Configuration
from src.crawler import Crawler
from src.views import (
    get_select_widget,
    get_entry_html,
    get_crawl_data,
    level2color,
    rssify,
    get_html,
)
from src import CrawlerContainer
from src.webtools import Url
from commandlineparser import CommandLineParser


app = Flask(__name__)


# should contain tuples of datetime, URL, properties
WebLogger.web_logger = PermanentLogger()
configuration = Configuration()
crawler_main = Crawler()


def get_crawlers():
    result = [""]

    config = configuration.get_crawler_config()
    for item in config:
        name = item["name"]
        result.append(name)

    return result


def get_handlers():
    handlers = [""]
    request = PageRequestObject("")
    for handler in Url(url="", request=request).get_handlers():
        handlers.append(handler.__name__)

    return handlers


def get_crawler_text():
    text = ""

    config = configuration.get_crawler_config()
    for item in config:
        name = item["name"]
        settings = item["settings"]
        text += "<div>Name:{} Settings:{}</div>\n".format(
            name, settings
        )

    return text


def get_crawling_form(title, action_url, id=""):
    crawlers = get_crawlers()
    handlers = get_handlers()

    crawler_select_html = get_select_widget("crawler_name", crawlers)
    handler_select_html = get_select_widget("handler_name", handlers)

    form_html = f"""
        <h1>{title}</h1>
        <form action="{action_url}?id={id}" method="get">
            <label for="url">URL</label><br>
            <input type="url" id="url" name="url" required autofocus><br><br>

            {crawler_select_html}
            {handler_select_html}

            <button type="submit">Submit</button>
        </form>
        """

    return form_html


def get_link_form(title, action_url, id=""):
    form_html = f"""
        <h1>{title}</h1>
        <form action="{action_url}?id={id}" method="get">
            <label for="url">URL:</label><br>
            <input type="text" id="url" name="url" required autofocus><br><br>
            <button type="submit">Submit</button>
        </form>
        """

    return form_html


@app.route("/")
def index():
    id = request.args.get("id")
    if not configuration.is_allowed(id):
        return get_html(id=id, body="Cannot access this view", title="Error")

    if not id:
        id = ""

    # fmt: off

    command_links = []
    command_links.append({"link" : "/info", "name":"Info", "description":"shows configuration"})
    command_links.append({"link" : "/infoj", "name":"Info JSON", "description":"configuration JSON information"})
    command_links.append({"link" : "/system", "name":"System monitoring", "description":"system monitoring"})

    operational_links = []
    operational_links.append({"link" : "/get", "name":"Get", "description":"form for getting web page crawl JSON information"})
    operational_links.append({"link" : "/getj", "name":"Get JSON", "description":"JSON crawling response"})
    operational_links.append({"link" : "/contents", "name":"Contents form", "description":"Form for getting web page contents"})
    operational_links.append({"link" : "/contentsr", "name":"Contents response", "description":"returns page contents, as if read by a browser"})
    operational_links.append({"link" : "/feeds", "name":"Feeds", "description":"form for finding feeds"})
    operational_links.append({"link" : "/feedsj", "name":"Feeds JSON", "description":"feeds information JSON"})
    operational_links.append({"link" : "/social", "name":"Social data", "description":"Social data form"})
    operational_links.append({"link" : "/socialj", "name":"Social data JSON", "description":"Social data JSON, likes"})
    operational_links.append({"link" : "/link", "name":"Link", "description":"form for obtaining links, canonical, etc."})
    operational_links.append({"link" : "/linkj", "name":"Link JSON", "description":"link information JSON"})
    operational_links.append({"link" : "/archivesj", "name":"Archive links JSON", "description":"JSON with links to archives, digital libraries"})
    operational_links.append({"link" : "/rssify", "name":"RSSify", "description":"form for RSSfication. RSSfication returns RSS contents for input link"})
    operational_links.append({"link" : "/rssifyr", "name":"RSSifyr", "description":"RSSfication response"})
    operational_links.append({"link" : "/ping", "name":"Ping", "description":"form for getting ping information"})
    operational_links.append({"link" : "/pingj", "name":"Ping JSON", "description":"JSON ping response"})
    operational_links.append({"link" : "/scanlinksj", "name":"Scan links", "description":"JSON for scannign links"})

    mgmt_links = []
    mgmt_links.append({"link" : "/history", "name":"History", "description":"crawl history"})
    mgmt_links.append({"link" : "/queue", "name":"Queue", "description":"shows current queue"})
    mgmt_links.append({"link" : "/find", "name":"Find", "description":"form for finding response"})
    mgmt_links.append({"link" : "/historyj", "name":"History JSON", "description":"shows history JSON"})
    mgmt_links.append({"link" : "/findj", "name":"Find JSON", "description":"returns information about history entry JSON"})
    mgmt_links.append({"link" : "/removej", "name":"Remove history", "description":"Removes history entry"})
    mgmt_links.append({"link" : "/debug", "name":"Debug", "description":"shows debug information"})

    # fmt: on

    text = """<h1>Commands</h1>"""

    for link_data in command_links:
        text += """<div><a href="{}?id={}">{}</a> - {}</div>""".format(
            link_data["link"], id, link_data["name"], link_data["description"]
        )

    text += "<h2>Operational</h2>"

    for link_data in operational_links:
        text += """<div><a href="{}?id={}">{}</a> - {}</div>""".format(
            link_data["link"], id, link_data["name"], link_data["description"]
        )

    text += "<h2>Management</h2>"

    for link_data in mgmt_links:
        text += """<div><a href="{}?id={}">{}</a> - {}</div>""".format(
            link_data["link"], id, link_data["name"], link_data["description"]
        )

    text += """<p>"""
    text += """Version:{}""".format(configuration.__version__)
    text += """</p>"""

    return get_html(id=id, body=text, title="Crawler Buddy", index=True)


@app.route("/info")
def info():
    id = request.args.get("id")
    if not configuration.is_allowed(id):
        return get_html(id=id, body="Cannot access this view", title="Error")

    text = """
    <h1>Crawlers</h1>
    """

    text += get_crawler_text()

    text += "<h2>Configuration</h2>"
    for key, value in configuration.data.items():
        text += "<div>{}:{}</div>".format(key, value)

    text += "<h2>System</h2>"
    size = crawler_main.container.get_size()
    records_size = crawler_main.container.records_size
    time_span = crawler_main.container.time_cache_m
    text += "<div>{}:{}</div>".format("History size", size)
    text += "<div>{}:{}</div>".format("Records size", records_size)
    text += "<div>{}:{}</div>".format("Time cache [m]", time_span)

    text += "<h2>System</h2>"
    process_count = webtools.WebConfig.count_chrom_processes()
    text += "<div>{}:{}</div>".format("Chrome processes", process_count)
    text += "<div>{}:{}</div>".format("Selenium count", webtools.SeleniumDriver.counter)

    chromedriver_path = Path("/usr/bin/chromedriver")
    if chromedriver_path.exists():
        text += "<div>Chromedriver at {} exists".format(chromedriver_path)
    else:
        text += "<div>Chromedriver at {} does not exist".format(chromedriver_path)

    return get_html(id=id, body=text, title="Configuration")


@app.route("/infoj")
def infoj():
    id = request.args.get("id")
    if not configuration.is_allowed(id):
        return get_html(id=id, body="Cannot access this view", title="Error")

    text = """
    <h1>Crawlers</h1>
    """

    all = {}
    crawlers = []
    properties = {}

    config = configuration.get_crawler_config()
    for item in config:
        crawlers.append(item)

    for aproperty, value in configuration.data.items():
        properties[str(aproperty)] = str(value)

    all["crawlers"] = crawlers
    all["properties"] = properties

    return jsonify(all)


@app.route("/history")
def history():
    id = request.args.get("id")
    if not configuration.is_allowed(id):
        return get_html(id=id, body="Cannot access this view", title="Error")

    text = ""

    text += "<h1>History</h1>\n"

    if crawler_main.container.get_size() == 0:
        text += "<div>No history yet!</div>"
    else:
        for crawl_data in reversed(crawler_main.container.container):
            crawl_type = crawl_data.crawl_type
            url = crawl_data.url
            timestamp = crawl_data.timestamp
            crawl_id = crawl_data.crawl_id

            if crawl_type == CrawlerContainer.CRAWL_TYPE_GET:
                all_properties = crawl_data.data
                entry_text = get_entry_html(id, crawl_id, url, timestamp, all_properties)
                text += entry_text
            else:
                text += get_crawl_data(id, crawl_data)

    return get_html(id=id, body=text, title="History")


@app.route("/historyj")
def historyj():
    id = request.args.get("id")
    if not configuration.is_allowed(id):
        return get_html(id=id, body="Cannot access this view", title="Error")

    json_history = []

    if crawler_main.container.get_size() == 0:
        return json_history

    for crawl_data in reversed(crawler_main.container.container):
        crawl_type = crawl_data.crawl_type
        url = crawl_data.url
        timestamp = crawl_data.timestamp
        crawl_id = crawl_data.crawl_id
        all_properties = crawl_data.data

        if crawl_type != CrawlerContainer.CRAWL_TYPE_GET:
            continue

        json_history.append(
            {"datetime": datetime, "url": url, "properties": all_properties}
        )

    return jsonify(json_history)


@app.route("/debug")
def debug():
    id = request.args.get("id")
    if not configuration.is_allowed(id):
        return get_html(id=id, body="Cannot access this view", title="Error")

    if not configuration.is_set("debug"):
        return get_html(id=id, body="Cannot access this view", title="Error")

    text = """
    <h1>Debug</h1>
    """

    for items in reversed(WebLogger.web_logger.permanent_data):
        level = items[0]
        timestamp = items[1]
        info_text = items[2]
        detail_text = items[3]
        user = items[4]

        if info_text:
            info_text = html.escape(info_text)

        color = level2color(level)

        text += '<div style="margin-bottom: 1em;">\n'
        text += f'<div>[{timestamp}] <span style="background-color:{color}">Level:{level}</span> info:{info_text}</div>\n'

        if detail_text:
            detail_text = html.escape(detail_text)
            text += "<pre>{}</pre>\n".format(detail_text)
        text += "</div>\n"

    return get_html(id=id, body=text, title="Debug")


@app.route("/set", methods=["POST"])
def set_response():
    data = request.json
    if not data or "Contents" not in data:
        return jsonify({"success": False, "error": "Missing 'Contents'"}), 400

    u = set_response_impl(request)

    p = u.handler.get_page_handler()

    all_properties = u.get_properties(full=True)

    crawler_main.container.add(crawl_type=CrawlerContainer.CRAWL_TYPE_GET, url=url, data=all_properties)

    return jsonify({"success": True, "received": contents})


def set_response_impl(request):
    # id = request.args.get("id")
    # if not configuration.is_allowed(id):
    #    return get_html(id=id, body="Cannot access this view", title="Error")

    data = request.json
    if not data or "Contents" not in data:
        return None

    # url = data['url']
    url = data["request_url"]
    contents = data["Contents"]
    headers = data["Headers"]
    status_code = data["status_code"]
    crawler_data = data["crawler_data"]
    crawler = crawler_data.get("crawler", None)
    if crawler and crawler == "ScriptCrawler":
        crawler_data["crawler"] = webtools.ScriptCrawler(url=url)

    content_bytes = base64.b64decode(contents)

    print("Server set_response:{}".format(url))

    response = PageResponseObject(
        url=url,
        headers=headers,
        binary=content_bytes,
        status_code=status_code,
        request_url=url,
    )

    u = webtools.Url(url, settings=crawler_data)
    u.settings = crawler_data
    u.handler = HttpPageHandler(url)
    u.handler.response = response

    return u


@app.route("/find", methods=["GET"])
def find():
    id = request.args.get("id")
    if not configuration.is_allowed(id):
        return get_html(id=id, body="Cannot access this view", title="Error")

    url = request.args.get("url")
    crawler_name = request.args.get("crawler_name")
    handler_name = request.args.get("handler_name")

    if not url and not crawler_name:
        form_html = get_crawling_form("Find", "/findj", id)

        return get_html(id=id, body=form_html, title="Find")
    else:
        crawler_data = crawler_main.container.get(
            url=url, crawler_name=name,
        )

        if not crawler_data:
            return get_html(
                id=id, body="Cannot find any entry matching data", title="Find"
            )

        index = crawler_data.crawl_id 
        timestamp = crawler_data.timestamp 
        all_properties = crawler_data.data 

        entry_text = get_entry_html(id, index, url, timestamp, all_properties)

        return get_html(id=id, body=entry_text, title=url)


@app.route("/findj", methods=["GET"])
def findj():
    id = request.args.get("id")
    if not configuration.is_allowed(id):
        return get_html(id=id, body="Cannot access this view", title="Error")

    url = request.args.get("url")
    name = request.args.get("crawler_name")
    index = request.args.get("index")

    if index:
        index = int(index)

    crawler_data = crawler_main.container.get(
        crawl_id=index, url=url, crawler_name=name,
    )

    if not crawler_data:
        return jsonify({"success": False, "error": "No properties found"}), 400

    index = crawler_data.crawl_id
    timestamp = crawler_data.timestamp
    all_properties = crawler_data.data

    if not all_properties:
        return jsonify({"success": False, "error": "No properties found"}), 400

    return jsonify(all_properties)


@app.route("/removej", methods=["GET"])
def removej():
    id = request.args.get("id")
    if not configuration.is_allowed(id):
        return get_html(id=id, body="Cannot access this view", title="Error")

    index = request.args.get("index")

    if index:
        index = int(index)

    if crawler_main.container.remove(crawl_id=index):
        return jsonify({"success": True})

    return jsonify({"success": False, "error": "Could not remove"}), 400


@app.route("/get", methods=["GET"])
def get():
    id = request.args.get("id")
    if not configuration.is_allowed(id):
        return get_html(id=id, body="Cannot access this view", title="Error")

    form_text = get_crawling_form("Get JSON information", "/getj", id)

    return get_html(id=id, body=form_text, title="Get")


@app.route("/getj", methods=["GET"])
def getj():
    id = request.args.get("id")
    if not configuration.is_allowed(id):
        return get_html(id=id, body="Cannot access this view", title="Error")

    all_properties = crawler_main.get_all_properties(request)
    if not all_properties:
        return (
            jsonify(
                {
                    "success": False,
                    "error": "Cannot convert to JSON: {}".format(str(all_properties)),
                }
            ),
            400,
        )

    return jsonify(all_properties)


@app.route("/rssify", methods=["GET"])
def rssify_this():
    id = request.args.get("id")
    if not configuration.is_allowed(id):
        return get_html(id=id, body="Cannot access this view", title="Error")

    form_text = get_crawling_form("Get RSS for link", "/rssifyr", id)

    return get_html(id=id, body=form_text, title="Get")


@app.route("/rssifyr", methods=["GET"])
def rssifyr():
    id = request.args.get("id")
    if not configuration.is_allowed(id):
        return get_html(id=id, body="Cannot access this view", title="Error")

    url = request.args.get("url")

    if not url:
        return jsonify({"success": False, "error": "No url provided"}), 400

    all_properties = crawler_main.get_all_properties(request)
    if all_properties:
        properties = CrawlerHistory.read_properties_section(
            "Properties", all_properties
        )
        entries = CrawlerHistory.read_properties_section("Entries", all_properties)

        if not entries or len(entries) == 0:
            if "feeds" in properties:
                for feed in properties["feeds"]:
                    all_properties = crawler_main.get_crawl_properties(
                        feed, crawler_data
                    )
                    if all_properties:
                        break

    return Response(rssify(all_properties), mimetype="application/rss+xml")


@app.route("/contents", methods=["GET"])
def contents():
    id = request.args.get("id")
    if not configuration.is_allowed(id):
        return get_html(id=id, body="Cannot access this view", title="Error")

    form_text = get_crawling_form("Get link contents", "/contentsr", id)

    return get_html(id=id, body=form_text, title="Get")


@app.route("/contentsr", methods=["GET"])
def contentsr():
    id = request.args.get("id")
    if not configuration.is_allowed(id):
        return get_html(id=id, body="Cannot access this view", title="Error")

    url = request.args.get("url")

    if not url:
        return jsonify({"success": False, "error": "No url provided"}), 400

    all_properties = crawler_main.get_all_properties(request)

    if not all_properties:
        return jsonify({"success": False, "error": "No properties found"}), 400

    page_url = RemoteUrl(url)
    page_url.all_properties = all_properties
    page_url.responses = {"Default" : RemoteServer.get_response(page_url.all_properties)}

    response = page_url.get_response()
    if response:
        status_code = response.get_status_code()
        content_type = response.get_contents_type()
    else:
        status_code = 600
        content_type = "text/html"

    return Response(contents, status=status_code, mimetype=content_type)


@app.route("/scanlinksj", methods=["GET"])
def scanlinksj():
    id = request.args.get("id")
    if not configuration.is_allowed(id):
        return get_html(id=id, body="Cannot access this view", title="Error")

    url = request.args.get("url")

    if not url:
        return jsonify({"success": False, "error": "No url provided"}), 400

    all_properties = crawler_main.get_all_properties(request)

    if not all_properties:
        return jsonify({"success": False, "error": "No properties found"}), 400

    page_url = RemoteUrl(url)
    page_url.all_properties = all_properties
    page_url.responses = {"Default" : RemoteServer.get_response(page_url.all_properties)}

    response = page_url.get_response()

    if response:
        parser = ContentLinkParser(url, response.get_text())

        return jsonify({"success": True, "links": list(parser.get_links())})
    return jsonify({"success": False, "error": "No response for link"}), 400


@app.route("/scandomainsj", methods=["GET"])
def scandomainsj():
    id = request.args.get("id")
    if not configuration.is_allowed(id):
        return get_html(id=id, body="Cannot access this view", title="Error")

    url = request.args.get("url")

    if not url:
        return jsonify({"success": False, "error": "No url provided"}), 400

    all_properties = crawler_main.get_all_properties(request)

    if not all_properties:
        return jsonify({"success": False, "error": "No properties found"}), 400

    page_url = RemoteUrl(url)
    page_url.all_properties = all_properties
    page_url.responses = {"Default" : RemoteServer.get_response(page_url.all_properties)}

    response = page_url.get_response()

    if response:
        parser = ContentLinkParser(url, response.get_text())

        return jsonify({"success": True, "links": list(parser.get_domains())})
    return jsonify({"success": False, "error": "No response for link"}), 400


@app.route("/headers", methods=["GET"])
def headers():
    # TODO implement
    id = request.args.get("id")
    if not configuration.is_allowed(id):
        return get_html(id=id, body="Cannot access this view", title="Error")

    url = request.args.get("url")

    if not url:
        return jsonify({"success": False, "error": "No url provided"}), 400

    all_properties = crawler_main.get_all_properties(request, headers=True)

    return jsonify(all_properties)


@app.route("/social", methods=["GET"])
def social():
    id = request.args.get("id")
    if not configuration.is_allowed(id):
        return get_html(id=id, body="Cannot access this view", title="Error")

    url = request.args.get("url")

    if not url:
        form_html = get_link_form("Find social information", "socialj", id)
        return get_html(id=id, body=form_html, title="Social")

    page_url = webtools.Url(url)

    text = "<h1>Social</h1>"

    for social_property, social_value in page_url.get_social_properties().items():
        text += f"<div>{social_property} {social_value}<div>".format(feed, feed)

    return get_html(id=id, body=text, title="Social")


@app.route("/socialj", methods=["GET"])
def socialj():
    """
    Dynamic, social data.
    Thumbs up, etc.
    """
    id = request.args.get("id")
    if not configuration.is_allowed(id):
        return get_html(id=id, body="Cannot access this view", title="Error")

    url = request.args.get("url")

    if not url:
        return jsonify({"success": False, "error": "No url provided"}), 400

    properties = crawler_main.get_social_properties(request, url)

    if properties:
        return jsonify(properties)
    else:
        return jsonify({})


@app.route("/ping", methods=["GET"])
def ping():
    id = request.args.get("id")
    if not configuration.is_allowed(id):
        return get_html(id=id, body="Cannot access this view", title="Error")

    url = request.args.get("url")

    if not url:
        form_html = get_link_form("Find ping information", "pingj", id)
        return get_html(id=id, body=form_html, title="Social")

    page_url = webtools.Url(url)

    text = "<h1>Ping</h1>"

    text += str(url.ping())

    return get_html(id=id, body=text, title="Social")


@app.route("/pingj", methods=["GET"])
def pingj():
    """
    Dynamic, social data.
    Thumbs up, etc.
    """
    id = request.args.get("id")
    if not configuration.is_allowed(id):
        return get_html(id=id, body="Cannot access this view", title="Error")

    url = request.args.get("url")
    if url:
        page_url = webtools.Url(url)
        response = page_url.ping()

        if response.is_valid():
            return jsonify({"status": True})

        if response.status_code == HTTP_STATUS_CODE_CONNECTION_ERROR:
            return jsonify({"status": False})

    all_properties = crawler_main.get_all_properties(request, ping=True)
    response = CrawlerHistory.read_properties_section("Response", all_properties)

    if response:
        status_code = response["status_code"]
        is_valid = response["is_valid"]
        return jsonify({"status": is_valid})

    return jsonify({"status": False})


@app.route("/linkj", methods=["GET"])
def linkj():
    id = request.args.get("id")
    if not configuration.is_allowed(id):
        return get_html(id=id, body="Cannot access this view", title="Error")

    url = request.args.get("url")

    if not url:
        return jsonify({"success": False, "error": "No url provided"}), 400

    page_url = webtools.Url(url)

    properties = {}
    properties["link"] = page_url.url
    properties["link_request"] = page_url.request_url
    properties["link_canonical"] = page_url.get_canonical_url()

    # TODO maybe we could add support for canonical links, maybe we could try reading fast, via requests?

    return jsonify(properties)


@app.route("/link", methods=["GET"])
def link():
    id = request.args.get("id")
    if not configuration.is_allowed(id):
        return get_html(id=id, body="Cannot access this view", title="Error")

    url = request.args.get("url")

    if not url:
        form_html = get_link_form("Get link information", "/linkj", id)
        return get_html(id=id, body=form_html, title="Feeds")

    page_url = webtools.Url(url)

    text = "<h1>Feeds</h1>"

    text += '<div>Link: <a href="{}">{}</a></div>'.format(page_url.url, page_url.url)
    text += '<div>Link request: <a href="{}">{}</a></div>'.format(
        page_url.request_url, page_url.request_url
    )
    text += '<div>Link canonical: <a href="{}">{}</a></div>'.format(
        page_url.get_canonical_url(), page_url.get_canonical_url()
    )

    # TODO maybe we could add support for canonical links, maybe we could try reading fast, via requests?

    return get_html(id=id, body=text, title="Error")


@app.route("/feedsj", methods=["GET"])
def feedsj():
    id = request.args.get("id")
    if not configuration.is_allowed(id):
        return get_html(id=id, body="Cannot access this view", title="Error")

    url = request.args.get("url")

    if not url:
        return jsonify({"success": False, "error": "No url provided"}), 400

    page_url = webtools.Url(url)

    properties = {"feeds": []}

    for feed in page_url.get_feeds():
        properties["feeds"].append(feed)

    # TODO maybe we could add support for canonical links, maybe we could try reading fast, via requests?

    return jsonify(properties)


@app.route("/feeds", methods=["GET"])
def feeds():
    id = request.args.get("id")
    if not configuration.is_allowed(id):
        return get_html(id=id, body="Cannot access this view", title="Error")

    url = request.args.get("url")

    if not url:
        form_html = get_link_form("Find feeds information", "feedsj", id)
        return get_html(id=id, body=form_html, title="Feeds")

    page_url = webtools.Url(url)

    text = "<h1>Feeds</h1>"

    for feed in page_url.get_feeds():
        text += '<div>Feed: <a href="{}">{}</a></div>'.format(feed, feed)

    # TODO maybe we could add support for canonical links, maybe we could try reading fast, via requests?

    return get_html(id=id, body=text, title="Error")


@app.route("/archivesj", methods=["GET"])
def archivesj():
    id = request.args.get("id")
    if not configuration.is_allowed(id):
        return get_html(id=id, body="Cannot access this view", title="Error")

    url = request.args.get("url")

    if not url:
        return jsonify({"success": False, "error": "No url provided"}), 400

    page_url = webtools.Url(url)

    properties = {"links": []}

    for archive_link in page_url.get_urls_archive():
        properties["links"].append(archive_link)

    # TODO maybe we could add support for canonical links, maybe we could try reading fast, via requests?

    return jsonify(properties)


def display_queue(container):
    text = ""
    for crawl_data in container.container:
        crawl_id = crawl_data.crawl_id
        crawl_type = crawl_data.crawl_type
        timestamp = crawl_data.timestamp
        url = crawl_data.url
        crawler_data = crawl_data.data

        if crawler_data is not None:
            continue

        timestamp_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")

        text += f'<div style="margin-bottom:1em;">[{timestamp_str}] {crawl_id} {crawl_type} {url} {request}</div>\n'

    return text


@app.route("/queue", methods=["GET"])
def queue():
    id = request.args.get("id")
    if not configuration.is_allowed(id):
        return get_html(id=id, body="Cannot access this view", title="Error")

    size = crawler_main.container.get_size()

    text = ""

    text += "<h1>Queue</h1>\n"
    text += display_queue(crawler_main.container)

    return get_html(id=id, body=text, title="Queue")


def dict_flat_to_html(data):
    html = ""
    for key, value in data.items():
        pair_html = "<strong>{}</strong>: {}".format(key, value)
        html += pair_html + ","

    return html


def dict_to_html(data, indent=0):
    html = ""
    for key, value in data.items():
        if isinstance(value, dict):
            html += (
                "  " * indent
                + f"<h{min(indent+2, 6)}>{key.capitalize()}</h{min(indent+2, 6)}>\n"
            )
            html += dict_to_html(value, indent + 1)
        elif isinstance(value, list):
            html += (
                "  " * indent
                + f"<h{min(indent+2, 6)}>{key.capitalize()}</h{min(indent+2, 6)}>\n"
            )
            html += "  " * indent + "<ul>\n"
            for item in value:
                if isinstance(item, dict):
                    html += "  " * (indent + 1) + "<li>\n"
                    html += dict_flat_to_html(item)
                    html += "  " * (indent + 1) + "</li>\n"
                else:
                    html += "  " * (indent + 1) + f"<li>{item}</li>\n"
            html += "  " * indent + "</ul>\n"
        else:
            html += "  " * indent + f"<p><strong>{key}:</strong> {value}</p>\n"
    return html


@app.route("/system", methods=["GET"])
def system():
    id = request.args.get("id")
    if not configuration.is_allowed(id):
        return get_html(id=id, body="Cannot access this view", title="Error")

    if not configuration.is_set("debug"):
        return get_html(id=id, body="Cannot access this view", title="Error")

    text = "<h1>System monitoring</h1>\n"

    info = get_hardware_info()
    info["processes"] = get_process_info()

    text = dict_to_html(info)

    return get_html(id=id, body=text, title="Processes")


if __name__ == "__main__":
    p = CommandLineParser()
    p.parse()

    history_length = p.args.history_length

    crawler_main.container.set_records_size(history_length)
    crawler_main.container.set_time_cache(p.args.time_cache_minutes)

    port = configuration.get("port")
    host = configuration.get("host")

    socket.setdefaulttimeout(40)

    if p.args.kill_processes and webtools.WebConfig.count_chrom_processes() > 0:
        print("Killing chrome processes")
        webtools.WebConfig.kill_chrom_processes()
        webtools.WebConfig.kill_xvfb_processes()
        print("Killing chrome processes DONE")

    webtools.WebConfig.disable_ssl_warnings()
    webtools.WebConfig.start_display()

    context = None
    if p.args.cert_file and p.args.cert_key:
        context = (p.args.cert_file, p.args.cert_key)

        app.run(
            debug=True,
            host=host,
            port=port,
            threaded=True,
            ssl_context=context,
        )
    else:
        app.run(debug=True, host=host, port=port, threaded=True)

    webtools.WebConfig.stop_display()
