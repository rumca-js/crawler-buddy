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
import argparse
import base64
import traceback
from datetime import datetime

from src import webtools
from src.configuration import Configuration
from src.crawler import Crawler
from src.viewutils import get_entry_html, level2color, rssify, get_html
from utils import PermanentLogger
from utils.systemmonitoring import get_hardware_info, get_process_info
from src import CrawlHistory


# increment major version digit for releases, or link name changes
# increment minor version digit for JSON data changes
# increment last digit for small changes
__version__ = "4.0.17"


app = Flask(__name__)


history_length = 200
# should contain tuples of datetime, URL, properties
social_history = CrawlHistory(history_length)
webtools.WebLogger.web_logger = PermanentLogger()
configuration = Configuration()
crawler_main = Crawler()


def get_crawler_text():
    text = ""

    config = configuration.get_crawler_config()
    for item in config:
        name = item["name"]
        crawler = item["crawler"]
        settings = item["settings"]
        text += "<div>Name:{} Crawler:{} Settings:{}</div>\n".format(
            name, crawler.__name__, settings
        )

    return text


def get_crawling_form(title, action_url, id=""):
    crawlers_text = get_crawler_text()

    form_html = f"""
        <h1>{title}</h1>
        <form action="{action_url}?id={id}" method="get">
            <label for="url">URL:</label><br>
            <input type="text" id="url" name="url" required><br><br>

            <label for="name">Name (optional):</label><br>
            <input type="text" id="name" name="name"><br><br>

            <label for="crawler">Crawler (optional):</label><br>
            <input type="text" id="crawler" name="crawler"><br><br>

            <button type="submit">Submit</button>
        </form>

        <h1>Available crawlers:</h1>
        <div style="margin-top:20px">
        {crawlers_text}
        </div>
        """

    return form_html


def get_link_form(title, action_url, id=""):
    form_html = f"""
        <h1>{title}</h1>
        <form action="{action_url}?id={id}" method="get">
            <label for="url">URL:</label><br>
            <input type="text" id="url" name="url" required><br><br>
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
    command_links.append({"link" : "/history", "name":"History", "description":"crawl history"})
    command_links.append({"link" : "/historyj", "name":"History JSON", "description":"shows history JSON"})
    command_links.append({"link" : "/debug", "name":"Debug", "description":"shows debug information"})

    operational_links = []
    operational_links.append({"link" : "/get", "name":"Get", "description":"form for getting web page crawl JSON information"})
    operational_links.append({"link" : "/getj", "name":"Get JSON", "description":"JSON crawling response"})
    operational_links.append({"link" : "/contents", "name":"Contents form", "description":"Form for getting web page contents"})
    operational_links.append({"link" : "/contentsr", "name":"Contents response", "description":"returns page contents, as if read by a browser"})
    operational_links.append({"link" : "/feeds", "name":"Feeds", "description":"form for finding feeds"})
    operational_links.append({"link" : "/feedsj", "name":"Feeds JSON", "description":"feeds information JSON"})
    operational_links.append({"link" : "/socialj", "name":"Social data JSON", "description":"Social data JSON, likes"})
    operational_links.append({"link" : "/link", "name":"Link", "description":"form for obtaining links, canonical, etc."})
    operational_links.append({"link" : "/linkj", "name":"Link JSON", "description":"link information JSON"})
    operational_links.append({"link" : "/archivesj", "name":"Archive links JSON", "description":"JSON with links to archives, digital libraries"})
    operational_links.append({"link" : "/rssify", "name":"RSSify", "description":"form for RSSfication. RSSfication returns RSS contents for input link"})
    operational_links.append({"link" : "/rssifyr", "name":"RSSifyr", "description":"RSSfication response"})

    mgmt_links = []
    mgmt_links.append({"link" : "/find", "name":"Find", "description":"form for finding response"})
    mgmt_links.append({"link" : "/findj", "name":"Find JSON", "description":"returns information about history entry JSON"})
    mgmt_links.append({"link" : "/queue", "name":"Queue", "description":"shows current queue"})
    mgmt_links.append({"link" : "/removej", "name":"Remove history", "description":"Removes history entry"})

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
    text += """Version:{}""".format(__version__)
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

    text += "<h2>Default user agent</h2>"
    text += "<div>Default user agent:{}</div>".format(
        webtools.crawlers.default_user_agent
    )

    text += "<h2>Default headers</h2>"
    for key in webtools.crawlers.default_headers:
        value = webtools.crawlers.default_headers[key]
        text += "<div>{}:{}</div>".format(key, value)

    return get_html(id=id, body=text, title="Configuration")


@app.route("/infoj")
def infoj():
    id = request.args.get("id")
    if not configuration.is_allowed(id):
        return get_html(id=id, body="Cannot access this view", title="Error")

    text = """
    <h1>Crawlers</h1>
    """

    properties = []

    config = configuration.get_crawler_config()
    for item in config:
        item["crawler"] = item["crawler"].__name__

        properties.append(item)

    return jsonify(properties)


@app.route("/history")
def history():
    id = request.args.get("id")
    if not configuration.is_allowed(id):
        return get_html(id=id, body="Cannot access this view", title="Error")

    text = ""

    text += "<h1>History</h1>\n"

    if crawler_main.get_history().get_history_size() == 0:
        text += "<div>No history yet!</div>"
    else:
        for datetime, index, things in reversed(crawler_main.get_history().container):
            url = things[0]
            all_properties = things[1]

            entry_text = get_entry_html(id, index, url, datetime, all_properties)

            text += entry_text

    return get_html(id=id, body=text, title="History")


@app.route("/historyj")
def historyj():
    id = request.args.get("id")
    if not configuration.is_allowed(id):
        return get_html(id=id, body="Cannot access this view", title="Error")

    json_history = []

    if crawler_main.get_history().get_history_size() == 0:
        return json_history

    for datetime, index, things in reversed(crawler_main.get_history().container):
        url = things[0]
        all_properties = things[1]

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

    for items in reversed(webtools.WebLogger.web_logger.permanent_data):
        level = items[0]
        timestamp = items[1]
        info_text = items[2]
        detail_text = items[3]
        user = items[4]

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

    crawler_main.get_history().add((url, all_properties))

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

    response = webtools.PageResponseObject(url = url, headers = headers, binary=content_bytes, status_code = status_code, request_url=url)

    u = webtools.Url(url, settings=crawler_data)
    u.settings = crawler_data
    u.handler = webtools.HttpPageHandler(url)
    u.handler.response = response

    return u


@app.route("/find", methods=["GET"])
def find():
    id = request.args.get("id")
    if not configuration.is_allowed(id):
        return get_html(id=id, body="Cannot access this view", title="Error")

    url = request.args.get("url")
    name = request.args.get("name")
    crawler = request.args.get("crawler")

    if not url and not name and not crawler:
        form_html = """
            <h1>Submit Your Details</h1>
            <form action="/findj?id={}" method="get">
                <label for="url">URL:</label><br>
                <input type="text" id="url" name="url" required><br><br>

                <label for="name">Name (optional):</label><br>
                <input type="text" id="name" name="name"><br><br>

                <label for="crawler">Crawler (optional):</label><br>
                <input type="text" id="crawler" name="crawler"><br><br>

                <button type="submit">Submit</button>
            </form>
            """.format(
            id
        )

        return get_html(id=id, body=form_html, title="Find")
    else:
        things = crawler_main.get_history().find(
            url=url, crawler_name=name, crawler=crawler
        )

        if not things:
            return get_html(
                id=id, body="Cannot find any entry matching data", title="Find"
            )

        index, timestamp, all_properties = things

        entry_text = get_entry_html(id, index, url, timestamp, all_properties)

        return get_html(id=id, body=entry_text, title=url)


@app.route("/findj", methods=["GET"])
def findj():
    id = request.args.get("id")
    if not configuration.is_allowed(id):
        return get_html(id=id, body="Cannot access this view", title="Error")

    url = request.args.get("url")
    name = request.args.get("name")
    crawler = request.args.get("crawler")
    index = request.args.get("index")

    if index:
        index = int(index)

    things = crawler_main.get_history().find(
        index=index, url=url, crawler_name=name, crawler=crawler
    )

    if not things:
        return jsonify({"success": False, "error": "No properties found"}), 400

    index, timestamp, all_properties = things

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

    if crawler_main.get_history().remove(index=index):
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

    url = request.args.get("url")

    if not url:
        return jsonify({"success": False, "error": "No url provided"}), 400

    crawler_data = crawler_main.get_request_data(request)

    if not crawler_data:
        return jsonify({"success": False, "error": "Cannot obtain crawler data"}), 400

    crawler_data["settings"]["headers"] = False
    crawler_data["settings"]["ping"] = False

    try:
        webtools.WebConfig.start_display()
        all_properties = crawler_main.get_crawl_properties(url, crawler_data)
    except Exception as E:
        webtools.WebLogger.exc(
            E, info_text="Exception when calling getj {} {}".format(url, crawler_data)
        )
        all_properties = None

    if not all_properties:
        return jsonify({"success": False, "error": "No properties found"}), 400

    try:
        return jsonify(all_properties)
    except:
        return (
            jsonify(
                {
                    "success": False,
                    "error": "Cannot convert to JSON: {}".format(str(all_properties)),
                }
            ),
            400,
        )


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

    crawler_data = crawler_main.get_request_data(request)

    if not crawler_data:
        return jsonify({"success": False, "error": "Cannot obtain crawler data"}), 400

    crawler_data["settings"]["headers"] = False
    crawler_data["settings"]["ping"] = False

    try:
        webtools.WebConfig.start_display()
        all_properties = crawler_main.get_crawl_properties(url, crawler_data)

        properties = CrawlHistory.read_properties_section("Properties", all_properties)
        entries = CrawlHistory.read_properties_section("Entries", all_properties)

        if not entries or len(entries) == 0:
            if "feeds" in properties:
                for feed in properties["feeds"]:
                    all_properties = crawler_main.get_crawl_properties(
                        feed, crawler_data
                    )
                    if all_properties:
                        break

    except Exception as E:
        webtools.WebLogger.exc(
            E, info_text="Exception when calling getj {} {}".format(url, crawler_data)
        )
        all_properties = None

    if not all_properties:
        return (
            jsonify({"success": False, "error": "No properties found - no properties"}),
            400,
        )

    entries = CrawlHistory.read_properties_section("Entries", all_properties)
    if not entries or len(entries) == 0:
        return (
            jsonify({"success": False, "error": "No entries found - no entries"}),
            400,
        )

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

    crawler_data = crawler_main.get_request_data(request)

    if not crawler_data:
        return jsonify({"success": False, "error": "Cannot obtain crawler data"}), 400

    crawler_data["settings"]["headers"] = False
    crawler_data["settings"]["ping"] = False

    all_properties = crawler_main.get_crawl_properties(url, crawler_data)

    if not all_properties:
        return jsonify({"success": False, "error": "No properties found"}), 400

    contents_data = CrawlHistory.read_properties_section("Text", all_properties)
    if "Contents" in contents_data:
        contents = contents_data["Contents"]
    else:
        contents = ""

    response = CrawlHistory.read_properties_section("Response", all_properties)
    if response:
        status_code = response["status_code"]
        content_type = response["Content-Type"]
    else:
        status_code = 600
        content_type = "text/html"

    return Response(contents, status=status_code, mimetype=content_type)


@app.route("/headers", methods=["GET"])
def headers():
    # TODO implement
    id = request.args.get("id")
    if not configuration.is_allowed(id):
        return get_html(id=id, body="Cannot access this view", title="Error")

    url = request.args.get("url")

    if not url:
        return jsonify({"success": False, "error": "No url provided"}), 400

    crawler_data = crawler_main.get_request_data(request)

    if not crawler_data:
        return jsonify({"success": False, "error": "Cannot obtain crawler data"}), 400

    crawler_data["settings"]["headers"] = True
    crawler_data["settings"]["ping"] = False

    all_properties = crawler_main.get_crawl_properties(url, crawler_data)

    if all_properties:
        crawler_main.get_history().add((url, all_properties))
    else:
        all_properties = crawler_main.get_history().find(url=url)

        if not all_properties:
            return jsonify({"success": False, "error": "No properties found"}), 400

    return jsonify(all_properties)


@app.route("/ping", methods=["GET"])
def ping():
    # TODO implement
    id = request.args.get("id")
    if not configuration.is_allowed(id):
        return get_html(id=id, body="Cannot access this view", title="Error")

    url = request.args.get("url")

    if not url:
        return jsonify({"success": False, "error": "No url provided"}), 400

    crawler_data = crawler_main.get_request_data(request)

    if not crawler_data:
        return jsonify({"success": False, "error": "Cannot obtain crawler data"}), 400

    crawler_data["settings"]["headers"] = False
    crawler_data["settings"]["ping"] = True

    all_properties = crawler_main.get_crawl_properties(url, crawler_data)

    if all_properties:
        crawler_main.get_history().add(url, all_properties)
    else:
        things = crawler_main.get_history().find(url=url)

        if not things:
            return jsonify({"success": False, "error": "No properties found"}), 400

        index, timestamp, all_properties = things

        if not all_properties:
            return jsonify({"success": False, "error": "No properties found"}), 400

    return jsonify(all_properties)


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

    things = social_history.find(url=url)
    if things:
        print("Reading from memory")
        index, timestamp, all_properties = things

        return jsonify(all_properties)

    page_url = webtools.Url(url)
    properties = page_url.get_social_properties()

    social_history.add((url, properties))

    return jsonify(properties)


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


@app.route("/queue", methods=["GET"])
def queue():
    id = request.args.get("id")
    if not configuration.is_allowed(id):
        return get_html(id=id, body="Cannot access this view", title="Error")

    size = crawler_main.crawler_info.get_size()

    text = """
    <div>Currently processing:{}</div>
    """.format(
        size
    )

    text += "<h1>Queue</h1>\n"

    for index in crawler_main.crawler_info.queue:
        things = crawler_main.crawler_info.queue[index]
        timestamp, url, crawler_data = things

        timestamp_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")

        text += '<div style="margin-bottom:1em;">{} {} {} {}</div>\n'.format(
            index, timestamp_str, url, crawler_data
        )

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


class CommandLineParser(object):
    """
    Headers can only be passed by input binary file
    """

    def parse(self):
        self.parser = argparse.ArgumentParser(description="Remote server options")
        self.parser.add_argument(
            "-l",
            "--history-length",
            default=200,
            type=int,
            help="Length of history",
        )
        self.parser.add_argument(
            "-t",
            "--time-cache-minutes",
            default=10,
            type=int,
            help="Time cache in minutes",
        )
        self.parser.add_argument("--cert-file", help="Host")
        self.parser.add_argument("--cert-key", help="Host")

        self.args = self.parser.parse_args()


if __name__ == "__main__":
    p = CommandLineParser()
    p.parse()

    history_length = p.args.history_length

    crawler_main.get_history().set_size(history_length)
    crawler_main.get_history().set_time_cache(p.args.time_cache_minutes)

    port = configuration.get("port")
    host = configuration.get("host")

    socket.setdefaulttimeout(40)

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
