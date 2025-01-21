"""
Starts server at the specified location

Access through:
    ip:port/crawlj?url=.... etc.
"""
from pathlib import Path
from flask import Flask, request, jsonify, Response
import socket
import json
import html
import subprocess
import argparse
from datetime import datetime
from collections import OrderedDict

from rsshistory import webtools
from utils import CrawlHistory


# increment major version digit for releases, or link name changes
# increment minor version digit for JSON data changes
# increment last digit for small changes
__version__ = "1.0.9"


app = Flask(__name__)


class CrawlerInfo(object):

    def __init__(self):
        self.queue = OrderedDict()
        self.crawl_index = 0

    def enter(self, url):
        self.queue[self.crawl_index] = datetime.now(), url

        if self.get_size() > 100:
            self.queue = OrderedDict()

        self.crawl_index += 1
        return self.crawl_index -1

    def leave(self, crawl_index):
        if crawl_index in self.queue:
            del self.queue[crawl_index]

    def get_size(self):
        return len(self.queue)


history_length = 200
# should contain tuples of datetime, URL, properties
url_history = CrawlHistory(history_length)
social_history = CrawlHistory(history_length)
crawler_info = CrawlerInfo()


def get_html(body, title="", index=False):
    if not index:
        body = '<a href="/">Back</a>' + body

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
    """.format(title, body)

    return html


def get_crawler_config():
    path = Path("init_browser_setup.json")
    if path.exists():
        print("Reading configuration from file")
        with path.open("r") as file:
            config = json.load(file)
            for index, item in enumerate(config):
                config[index]["crawler"] = webtools.WebConfig.get_crawler_from_string(item["crawler"])

            return config
    else:
        print("Reading configuration from webtools")
        return webtools.WebConfig.get_init_crawler_config()


def get_crawler(name = None, crawler_name = None):
    config = get_crawler_config()
    for item in config:
        if name:
            if name == item["name"]:
                return item
        if crawler_name:
            if crawler_name == item["crawler"].__name__:
                return item


def run_webtools_url(url, crawler_data = None):

    # this is something new

    page_url = webtools.Url(url)
    options = page_url.get_init_page_options()

    full = crawler_data["settings"]["full"]
    request_headers = crawler_data["settings"]["headers"]
    request_ping = crawler_data["settings"]["ping"]

    remote_server = crawler_data["settings"]["remote_server"]

    new_mapping = None

    if "crawler" not in crawler_data and "name" in crawler_data:
        new_mapping = get_crawler(name = crawler_data["name"])
    elif "name" not in crawler_data and "crawler" in crawler_data:
        new_mapping = get_crawler(crawler_name = crawler_data["crawler"])
    elif "name" not in crawler_data and "crawler" not in crawler_data:
        pass
    else:
        new_mapping = crawler_data
        new_mapping["crawler"] = webtools.WebConfig.get_crawler_from_string(new_mapping["crawler"])

    if new_mapping:
        if new_mapping["settings"] is None:
            new_mapping["settings"] = {}
        new_mapping["settings"]["remote-server"] = remote_server

        print("Running:{}, with:{}".format(url, new_mapping))

        options.mode_mapping = [new_mapping]

    page_url = webtools.Url(url, page_options=options)

    if request_headers:
        # TODO implement
        headers = page_url.get_headers()
        all_properties = [
                { "name" : "Headers",
                  "data" : headers }
        ]
    elif request_ping:
        # TODO implement
        headers = page_url.get_headers()
        all_properties = [
                { "name" : "Headers",
                  "data" : headers }
        ]
    else:
        # TODO what if there is exception
        crawl_index = crawler_info.enter(url)

        response = page_url.get_response()

        all_properties = page_url.get_properties(full=True, include_social=full)

        crawler_info.leave(crawl_index)

    return all_properties


@app.route('/')
def home():
    text = """
    <h1>Commands</h1>
    <div><a href="/info">Info</a> - shows configuration</div>
    <div><a href="/infoj">Info JSON</a> - shows configuration JSON</div>
    <div><a href="/history">History</a> - shows history</div>
    <div><a href="/historyj">History JSON</a> - shows JSON history</div>
    <div><a href="/queue">Queue</a> - shows currently processing queue</div>
    <div><a href="/find">find</a> - form for findj</div>
    <div><a href="/findj">find JSON</a> - returns information about history entry JSON</div>
    <div><a href="/crawl">Crawl</a> - form for crawlj</div>
    <div><a href="/crawlj">Crawlj</a> - crawl a web page</div>
    <div><a href="/socialj">Socialj</a> - dynamic, social data JSON</div>
    <div><a href="/proxy">Proxy</a> - makes GET request, then passes you the contents, as is</div>
    <p>
    Version:{}
    </p>
    """.format(__version__)

    return get_html(body = text, title = "Crawler Buddy", index=True)


@app.route('/info')
def info():
    text = """
    <h1>Crawlers</h1>
    """

    config = get_crawler_config()
    for item in config:
        name = item["name"]
        crawler = item["crawler"]
        settings = item["settings"]
        text += "<div>Name:{} Crawler:{} Settings:{}</div>".format(name, crawler.__name__, settings)

    return get_html(body = text, title="Configuration")


@app.route('/infoj')
def infoj():
    text = """
    <h1>Crawlers</h1>
    """

    properties = []

    config = get_crawler_config()
    for item in config:
        item["crawler"] = item["crawler"].__name__

        properties.append(item)

    return jsonify(properties)


def get_entry_html(index, url, all_properties):
    text = ""

    link = "/findj?index=" + str(index)

    text += """<a href="{}"><h2>{} {}</h2></a>""".format(link, datetime, url)

    contents_data = CrawlHistory.read_properties_section("Contents", all_properties)
    if "Contents" in contents_data:
        contents = contents_data["Contents"]
    else:
        contents = ""

    response = CrawlHistory.read_properties_section("Response", all_properties)
    if response:
        status_code = response["status_code"]
        charset = response["Charset"]
        content_length = response["Content-Length"]
        content_type = response["Content-Type"]
        if "crawler_data" in response and response["crawler_data"] and "name" in response["crawler_data"]:
            crawler_name = response["crawler_data"]["name"]
        else:
            crawler_name = ""
        if "crawler_data" in response and response["crawler_data"] and "crawler" in response["crawler_data"]:
            crawler_crawler = response["crawler_data"]["crawler"]
        else:
            crawler_crawler = ""
    else:
        status_code = ""
        charset = ""
        content_length = ""
        content_type = ""
        crawler_name = ""

    text += "<div>Status code:{} charset:{} Content-Type:{} Content-Length:{} Crawler name:{} Crawler:{}</div>".format(status_code, charset, content_type, content_length, crawler_name, crawler_crawler)

    return text


@app.route('/history')
def history():
    text = ""

    text += "<h1>History</h1>"

    if url_history.get_history_size() == 0:
        text += "<div>No history yet!</div>"
    else:
        for datetime, index, things in reversed(url_history.container):
            url = things[0]
            all_properties = things[1]

            entry_text = get_entry_html(index, url, all_properties)

            text += entry_text

    return get_html(body = text, title="History")


@app.route('/historyj')
def historyj():
    json_history = []

    if url_history.get_history_size() == 0:
        return json_history

    for datetime, index, things in reversed(url_history.container):
        url = things[0]
        all_properties = things[1]

        json_history.append(
                {"datetime" : datetime,
                 "url" : url,
                 "properties" : all_properties }
                )

    return jsonify(json_history)


@app.route('/set', methods=['POST'])
def set_response():
    data = request.json
    if not data or 'Contents' not in data:
        return jsonify({"success": False, "error": "Missing 'Contents'"}), 400

    # url = data['url']
    url = data['request_url']
    contents = data['Contents']
    headers = data['Headers']
    status_code = data['status_code']

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
    all_properties.append({"name": "Contents", "data" : {"Contents" : contents}})
    all_properties.append({})
    all_properties.append({"name" : "Response", "data" : response})
    all_properties.append({"name" : "Headers", "data" : headers})

    if len(url_history) > history_length:
        url_history.pop(0)

    url_history.add( (url, all_properties) )

    return jsonify({"success": True, "received": contents})


@app.route('/find', methods=['GET'])
def find():
    url = request.args.get('url')
    name = request.args.get('name')
    crawler = request.args.get('crawler')

    if not url and not name and not crawler:
        form_html = '''
            <h1>Submit Your Details</h1>
            <form action="/findj" method="get">
                <label for="url">URL:</label><br>
                <input type="text" id="url" name="url" required><br><br>

                <label for="name">Name (optional):</label><br>
                <input type="text" id="name" name="name"><br><br>

                <label for="crawler">Crawler (optional):</label><br>
                <input type="text" id="crawler" name="crawler"><br><br>

                <button type="submit">Submit</button>
            </form>
            '''

        return get_html(form_html)
    else:
        things = url_history.find(url = url, crawler_name = name, crawler = crawler)

        if not things:
            return get_html("Cannot find any entry matching data")

        index, all_properties = things

        entry_text = get_entry_html(index, url, all_properties)

        return get_html(entry_text)


@app.route('/findj', methods=['GET'])
def findj():
    url = request.args.get('url')
    name = request.args.get('name')
    crawler = request.args.get('crawler')
    index = request.args.get('index')

    if index:
        index = int(index)

    things = url_history.find(index = index, url = url, crawler_name = name, crawler = crawler)

    if not things:
        return jsonify({
            "success": False,
            "error": "No properties found"
        }), 400


    index, all_properties = things

    if not all_properties:
        return jsonify({
            "success": False,
            "error": "No properties found"
        }), 400

    return jsonify(all_properties)


def get_request_data(request):
    crawler_data = request.args.get('crawler_data')
    crawler = request.args.get('crawler')
    name = request.args.get('name')

    parsed_crawler_data = None
    if crawler_data:
        try:
            parsed_crawler_data = json.loads(crawler_data)
        except json.JSONDecodeError as E:
            print(str(E))

    if parsed_crawler_data is None:
        parsed_crawler_data = {}

    if crawler:
        parsed_crawler_data["crawler"] = crawler
    if name:
        parsed_crawler_data["name"] = name

    if "settings" not in parsed_crawler_data:
        parsed_crawler_data["settings"] = {}

    remote_server = f"http://{request.host}"

    parsed_crawler_data["settings"]["remote_server"] = remote_server

    return parsed_crawler_data


def get_crawl_properties(url, crawler_data):
    name = None
    if "name" in crawler_data:
        name = crawler_data["name"]
    crawler = None
    if "crawler" in crawler_data:
        crawler = crawler_data["crawler"]

    things = url_history.find(url = url, crawler_name = name, crawler = crawler)
    print("Returning from saved properties")

    if things:
        index, all_properties = things

        if all_properties:
            return all_properties

    all_properties = run_webtools_url(url, crawler_data)

    if all_properties:
        url_history.add( (url, all_properties) )
    else:
        all_properties = find_response(url)

    return all_properties


@app.route('/crawl', methods=['GET'])
def crawl():
    form_html = '''
        <h1>Submit Your Details</h1>
        <form action="/crawlj" method="get">
            <label for="url">URL:</label><br>
            <input type="text" id="url" name="url" required><br><br>

            <label for="name">Name (optional):</label><br>
            <input type="text" id="name" name="name"><br><br>

            <label for="crawler">Crawler (optional):</label><br>
            <input type="text" id="crawler" name="crawler"><br><br>

            <button type="submit">Submit</button>
        </form>
        '''

    return get_html(form_html)


@app.route('/crawlj', methods=['GET'])
def crawlj():
    url = request.args.get('url')
    full = request.args.get('full')

    if not url:
        return jsonify({
            "success": False,
            "error": "No url provided"
        }), 400

    crawler_data = get_request_data(request)

    crawler_data["settings"]["full"] = full
    crawler_data["settings"]["headers"] = False
    crawler_data["settings"]["ping"] = False

    all_properties = get_crawl_properties(url, crawler_data)

    if not all_properties:
        return jsonify({
            "success": False,
            "error": "No properties found"
        }), 400

    return jsonify(all_properties)


@app.route('/proxy', methods=['GET'])
def proxy():
    url = request.args.get('url')
    full = request.args.get('full')

    if not url:
        return jsonify({
            "success": False,
            "error": "No url provided"
        }), 400

    crawler_data = get_request_data(request)

    crawler_data["settings"]["full"] = full
    crawler_data["settings"]["headers"] = False
    crawler_data["settings"]["ping"] = False

    all_properties = get_crawl_properties(url, crawler_data)

    if not all_properties:
        return jsonify({
            "success": False,
            "error": "No properties found"
        }), 400

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


@app.route('/headers', methods=['GET'])
def headers():
    # TODO implement
    url = request.args.get('url')
    full = request.args.get('full')

    if not url:
        return jsonify({
            "success": False,
            "error": "No url provided"
        }), 400

    crawler_data = get_request_data(request)

    crawler_data["settings"]["full"] = full
    crawler_data["settings"]["headers"] = True
    crawler_data["settings"]["ping"] = False

    all_properties = get_crawl_properties(url, crawler_data)

    if all_properties:
        if len(url_history) > history_length:
            url_history.pop(0)

        url_history.add( (url, all_properties) )
    else:
        all_properties = find_response(url)

        if not all_properties:
            return jsonify({
                "success": False,
                "error": "No properties found"
            }), 400

    return jsonify(all_properties)


@app.route('/ping', methods=['GET'])
def ping():
    # TODO implement
    url = request.args.get('url')
    full = request.args.get('full')

    if not url:
        return jsonify({
            "success": False,
            "error": "No url provided"
        }), 400

    crawler_data = get_request_data(request)

    crawler_data["settings"]["full"] = full
    crawler_data["settings"]["headers"] = False
    crawler_data["settings"]["ping"] = True

    all_properties = get_crawl_properties(url, crawler_data)

    if all_properties:
        url_history.add(url, all_properties)
    else:
        index, all_properties = url_history.find(url = url)

        if not all_properties:
            return jsonify({
                "success": False,
                "error": "No properties found"
            }), 400

    return jsonify(all_properties)


@app.route('/socialj', methods=['GET'])
def socialj():
    """
    Dynamic, social data.
    Thumbs up, etc.
    """
    url = request.args.get('url')

    if not url:
        return jsonify({
            "success": False,
            "error": "No url provided"
        }), 400

    things = social_history.find(url = url)
    if things:
        print("Reading from memory")
        index = things[0]
        properties = things[1]
        return jsonify(properties)

    page_url = webtools.Url(url)
    properties = page_url.get_social_properties()

    social_history.add((url, properties))

    return jsonify(properties)


@app.route('/queue', methods=['GET'])
def queue():
    size = crawler_info.get_size()

    text = """
    <div>Currently processing:{}</div>
    """.format(size)

    text += "<h1>Queue</h1>"

    for index in crawler_info.queue:
        timestamp, url = crawler_info.queue[index]

        text += "<div>{} {} {}</div>".format(index, timestamp, url)

    return get_html(text)



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
            "-l", "--history-length", default=200, type=int, help="Length of history",
        )
        self.parser.add_argument(
            "-t", "--time-cache-minutes", default=10, type=int, help="Time cache in minutes"
        )
        self.parser.add_argument("--host", default="0.0.0.0", help="Host")

        self.args = self.parser.parse_args()


if __name__ == '__main__':
    p = CommandLineParser()
    p.parse()

    history_length = p.args.history_length
    url_history.set_size(history_length)
    url_history.set_time_cache(p.args.time_cache_minutes)

    socket.setdefaulttimeout(40)

    app.run(debug=True, host=p.args.host, port=p.args.port, threaded=True)
