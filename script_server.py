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
import traceback
from datetime import datetime

from rsshistory import webtools
from rsshistory.configuration import Configuration
from rsshistory.crawler import Crawler
from utils import CrawlHistory, PermanentLogger


# increment major version digit for releases, or link name changes
# increment minor version digit for JSON data changes
# increment last digit for small changes
__version__ = "2.0.9"


app = Flask(__name__)


history_length = 200
# should contain tuples of datetime, URL, properties
url_history = CrawlHistory(history_length)
social_history = CrawlHistory(history_length)
webtools.WebLogger.web_logger = PermanentLogger()
configuration = Configuration()
crawler_main = Crawler()


def get_html(id, body, title="", index=False):
    if not index:
        if not id:
            id = ""
        body = '<a href="/?id={}">Back</a>'.format(id) + body

    html = """<!DOCTYPE html>
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>{}</title>
    </head>
    <body>
    {}
    </body>
    </html>
    """.format(
        title, body
    )

    return html


def get_entry_html(id, index, url, timestamp, all_properties):
    text = ""

    if not id:
        id = ""
    link = "/findj?id={}&index={}".format(id, str(index))

    timestamp_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")

    text += """<a href="{}"><h2>[{}] {}</h2></a>""".format(link, timestamp_str, url)

    contents = ""
    contents_data = CrawlHistory.read_properties_section("Contents", all_properties)
    if contents_data and "Contents" in contents_data:
        contents = contents_data["Contents"]

    response = CrawlHistory.read_properties_section("Response", all_properties)
    options = CrawlHistory.read_properties_section("Options", all_properties)
    if response:
        status_code = response["status_code"]
        # TODO maybe create a better API
        status_code = webtools.status_code_to_text(status_code)

        charset = response["Charset"]
        content_length = response["Content-Length"]
        content_type = response["Content-Type"]

        if (options
            and "name" in options
        ):
            crawler_name = options["name"]
        else:
            crawler_name = ""
        if (
            options
            and "crawler" in options
        ):
            crawler_crawler = options["crawler"]
        else:
            crawler_crawler = ""
    else:
        status_code = ""
        charset = ""
        content_length = ""
        content_type = ""
        crawler_name = ""
        crawler_crawler = ""

    text += "<div>Status code:{} charset:{} Content-Type:{} Content-Length:{} Crawler name:{} Crawler:{}</div>".format(
        status_code,
        charset,
        content_type,
        content_length,
        crawler_name,
        crawler_crawler,
    )

    return text




def get_crawl_properties(url, crawler_data):
    name = None
    if "name" in crawler_data:
        name = crawler_data["name"]
    crawler = None
    if "crawler" in crawler_data:
        crawler = crawler_data["crawler"]

    things = url_history.find(url=url, crawler_name=name, crawler=crawler)
    print("Returning from saved properties")

    if things:
        index, timestamp, all_properties = things

        if all_properties:
            return all_properties

    all_properties = crawler_main.run(url, crawler_data)

    if all_properties:
        url_history.add((url, all_properties))
    else:
        all_properties = url_history.find(url=url)

    return all_properties


@app.route("/")
def index():
    id = request.args.get("id")
    if not configuration.is_allowed(id):
        return get_html(id=id, body="Cannot access this view", title="Error")

    text = """
    <h1>Commands</h1>
    """

    if not id:
        id = ""

    text += (
        """<div><a href="/info?id={}">Info</a> - shows configuration</div>""".format(id)
    )
    text += """<div><a href="/infoj?id={}">Info JSON</a> - shows configuration JSON</div>""".format(id)
    text += (
        """<div><a href="/history?id={}">History</a> - shows history</div>""".format(id)
    )
    text += """<div><a href="/historyj?id={}">History JSON</a> - shows JSON history</div>""".format(id)
    text += """<div><a href="/queue?id={}">Queue</a> - shows currently processing queue</div>""".format( id)
    text += """<div><a href="/find?id={}">Find</a> - form for findj</div>""".format(id)
    text += """<div><a href="/findj?id={}">Find JSON</a> - returns information about history entry JSON</div>""".format(id)
    text += """<div><a href="/get?id={}">Get</a> - form for crawling a web page using GET method</div>""".format(id)
    text += """<div><a href="/getj?id={}">Getj</a> - crawl a web page using GET method</div>""".format(id)
    text += """<div><a href="/socialj?id={}">Socialj</a> - dynamic social data JSON</div>""".format(id)
    text += """<div><a href="/proxy?id={}">Proxy</a> - makes GET request, then passes you the contents, as is</div>""".format(id)
    text += """<div><a href="/linkj?id={}">Linkj</a> - return link info JSON</div>""".format(id)
    text += """<div><a href="/feedsj?id={}">Feedsj</a> - return feeds info JSON</div>""".format(id)
    text += """<div><a href="/archivesj?id={}">Archivesj</a> - return archive links info JSON</div>""".format(id)

    if configuration.is_set("debug"):
        text += """<div><a href="/debug?id={}">Debug</a> - shows debug information</div>""".format(id)

    if configuration.is_set("debug"):
        text += """<div><a href="/processes?id={}">Processes</a> - shows processes</div>""".format(id)

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

    config = configuration.get_crawler_config()
    for item in config:
        name = item["name"]
        crawler = item["crawler"]
        settings = item["settings"]
        text += "<div>Name:{} Crawler:{} Settings:{}</div>".format(
            name, crawler.__name__, settings
        )

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

    text += "<h1>History</h1>"

    if url_history.get_history_size() == 0:
        text += "<div>No history yet!</div>"
    else:
        for datetime, index, things in reversed(url_history.container):
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

    if url_history.get_history_size() == 0:
        return json_history

    for datetime, index, things in reversed(url_history.container):
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

        text += '<div style="display: flex; flex-direction: column; gap: 0.2em;">'
        text += '<div>[{}] Level:{} info:{}</div>'.format(timestamp, level, info_text)
        if detail_text:
            detail_text = html.escape(detail_text)
            text += "<div>{}</div>".format(detail_text)
        text += "</div>"

    return get_html(id=id, body=text, title="Debug")


@app.route("/set", methods=["POST"])
def set_response():
    #id = request.args.get("id")
    #if not configuration.is_allowed(id):
    #    return get_html(id=id, body="Cannot access this view", title="Error")

    data = request.json
    if not data or "Contents" not in data:
        return jsonify({"success": False, "error": "Missing 'Contents'"}), 400

    # url = data['url']
    url = data["request_url"]
    contents = data["Contents"]
    headers = data["Headers"]
    status_code = data["status_code"]

    print("Received data about {}".format(url))

    response = {}
    if headers and "Charset" in headers:
        response["Charset"] = headers["Charset"]
    else:
        response["Charset"] = None
    if headers and "Content-Length" in headers:
        response["Content-Length"] = headers["Content-Length"]
    else:
        response["Content-Length"] = None

    if headers and "Content-Type" in headers:
        response["Content-Type"] = headers["Content-Type"]
    else:
        response["Content-Type"] = None

    response["status_code"] = status_code

    all_properties = []
    all_properties.append({})
    all_properties.append({"name": "Contents", "data": {"Contents": contents}})
    all_properties.append({})
    all_properties.append({"name": "Response", "data": response})
    all_properties.append({"name": "Headers", "data": headers})

    url_history.add((url, all_properties))

    return jsonify({"success": True, "received": contents})


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
        things = url_history.find(url=url, crawler_name=name, crawler=crawler)

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

    things = url_history.find(index=index, url=url, crawler_name=name, crawler=crawler)

    if not things:
        return jsonify({"success": False, "error": "No properties found"}), 400

    index, timestamp, all_properties = things

    if not all_properties:
        return jsonify({"success": False, "error": "No properties found"}), 400

    return jsonify(all_properties)


@app.route("/get", methods=["GET"])
def get():
    id = request.args.get("id")
    if not configuration.is_allowed(id):
        return get_html(id=id, body="Cannot access this view", title="Error")

    form_html = """
        <h1>Submit Your Details</h1>
        <form action="/getj?id={}" method="get">
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

    return get_html(id=id, body=form_html, title="Crawl")


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
        all_properties = get_crawl_properties(url, crawler_data)
    except Exception as E:
        webtools.WebLogger.exc(E, info_text="Exception when calling getj {} {}".format(url, crawler_data))
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


@app.route("/proxy", methods=["GET"])
def proxy():
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

    all_properties = get_crawl_properties(url, crawler_data)

    if not all_properties:
        return jsonify({"success": False, "error": "No properties found"}), 400

    contents_data = CrawlHistory.read_properties_section("Contents", all_properties)
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

    all_properties = get_crawl_properties(url, crawler_data)

    if all_properties:
        url_history.add((url, all_properties))
    else:
        all_properties = url_history.find(url=url)

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

    all_properties = get_crawl_properties(url, crawler_data)

    if all_properties:
        url_history.add(url, all_properties)
    else:
        things = url_history.find(url=url)

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


@app.route("/feedsj", methods=["GET"])
def feedsj():
    id = request.args.get("id")
    if not configuration.is_allowed(id):
        return get_html(id=id, body="Cannot access this view", title="Error")

    url = request.args.get("url")

    if not url:
        return jsonify({"success": False, "error": "No url provided"}), 400

    page_url = webtools.Url(url)

    properties = {"feeds" : []}

    for feed in page_url.get_feeds():
        properties["feeds"].append(feed)

    # TODO maybe we could add support for canonical links, maybe we could try reading fast, via requests?

    return jsonify(properties)


@app.route("/archivesj", methods=["GET"])
def archivesj():
    id = request.args.get("id")
    if not configuration.is_allowed(id):
        return get_html(id=id, body="Cannot access this view", title="Error")

    url = request.args.get("url")

    if not url:
        return jsonify({"success": False, "error": "No url provided"}), 400

    page_url = webtools.Url(url)

    properties = {"links" : []}

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

    text += "<h1>Queue</h1>"

    for index in crawler_main.crawler_info.queue:
        things = crawler_main.crawler_info.queue[index]
        timestamp, url, crawler_data = things

        timestamp_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")
        
        text += '<div style="display: flex; flex-direction: column; gap: 0.2em;">'
        text += "<div>{} {} {} {}</div>".format(index, timestamp_str, url, crawler_data)
        text += "</div>"

    return get_html(id=id, body=text, title="Queue")


@app.route("/processes", methods=["GET"])
def processes():
    id = request.args.get("id")
    if not configuration.is_allowed(id):
        return get_html(id=id, body="Cannot access this view", title="Error")

    if not configuration.is_set("debug"):
        return get_html(id=id, body="Cannot access this view", title="Error")

    process = subprocess.run(["top", "-b", "-n", "1"], capture_output=True, text=True)

    out = process.stdout

    lines = out.split("\n")

    text = "<h1>Chrome processes</h1>"
    text += "<div>Number of chrom processes {}</div>".format(
        webtools.WebConfig.count_chrom_processes()
    )

    text += "<h1>Processes</h1>"

    for line in lines:
        text += "<div>{}</div>".format(line)

    return get_html(id=id, body=text, title="Processes")


class CommandLineParser(object):
    """
    Headers can only be passed by input binary file
    """

    def parse(self):
        self.parser = argparse.ArgumentParser(description="Remote server options")
        self.parser.add_argument(
            "--port", default=3000, type=int, help="Port number to be used"
        )
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
        self.parser.add_argument("--host", default="0.0.0.0", help="Host")
        self.parser.add_argument("--cert-file", help="Host")
        self.parser.add_argument("--cert-key", help="Host")

        self.args = self.parser.parse_args()


if __name__ == "__main__":
    p = CommandLineParser()
    p.parse()

    history_length = p.args.history_length
    url_history.set_size(history_length)
    url_history.set_time_cache(p.args.time_cache_minutes)

    socket.setdefaulttimeout(40)

    webtools.WebConfig.start_display()

    context = None
    if p.args.cert_file and p.args.cert_key:
        context = (p.args.cert_file, p.args.cert_key)

        app.run(debug=True, host=p.args.host, port=p.args.port, threaded=True, ssl_context=context)
    else:
        app.run(debug=True, host=p.args.host, port=p.args.port, threaded=True)

    webtools.WebConfig.stop_display()
