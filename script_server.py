"""
Starts flask server at the specified location.

Access through:
    ip:port/run?url=.... etc.

Examples:
http://127.0.0.1:3000/run?url=https://google.com&crawler_data={"crawler":"StealthRequestsCrawler","name":"StealthRequestsCrawler","settings": {"timeout_s":20}}
http://127.0.0.1:3000/run?url=https://google.com&crawler_data={"crawler":"SeleniumChromeFull","name":"SeleniumChromeFull","settings": {"timeout_s":50, "driver_executable" : "/usr/bin/chromedriver"}}
http://127.0.0.1:3000/run?url=https://google.com&crawler_data={"crawler":"ScriptCrawler","name":"CrawleeScript","settings": {"timeout_s":50, "script" : "poetry run python crawleebeautifulsoup.py"}}
http://127.0.0.1:3000/run?url=https://google.com&crawler_data={"crawler":"ScriptCrawler","name":"CrawleeScript","settings": {"timeout_s":50, "script" : "poetry run python crawleebeautifulsoup.py", "remote-server" : "http://127.0.0.1:3000"}}
"""
from pathlib import Path
from flask import Flask, request, jsonify
import json
import html
import subprocess
import argparse
from datetime import datetime

from rsshistory import webtools


app = Flask(__name__)


# should contain tuples of datetime, URL, properties
url_history = []
history_length = 200


def get_html(body, index=False):
    if not index:
        body = '<a href="/">Back</a>' + body

    html = """<!DOCTYPE html>
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1">
    </head>
    <body>
    {}
    </body>
    </html>
    """.format(body)

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


def find_response(input_url):
    for datetime, url, all_properties in reversed(url_history):
        if input_url == url and all_properties:
            return all_properties


def run_webtools_url(url, crawler_data):
    page_url = webtools.Url(url)
    options = page_url.get_init_page_options()
    full = crawler_data["settings"]["full"]
    request_headers = crawler_data["settings"]["headers"]
    request_ping = crawler_data["settings"]["ping"]

    remote_server = crawler_data["settings"]["remote_server"]

    if crawler_data:
        if "crawler" in crawler_data:
            crawler_data["crawler"] = webtools.WebConfig.get_crawler_from_string(crawler_data["crawler"])

            if crawler_data["settings"] is None:
                crawler_data["settings"] = {}
            crawler_data["settings"]["remote-server"] = remote_server

            options.mode_mapping = [crawler_data]

        if "name" in crawler_data:
            config = get_crawler_config()
            for item in config:
                if crawler_data["name"] == item["name"]:
                    crawler_data = item

                    if crawler_data["settings"] is None:
                        crawler_data["settings"] = {}
                    crawler_data["settings"]["remote-server"] = remote_server

                    options.mode_mapping = [crawler_data]

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
        response = page_url.get_response()
        all_properties = page_url.get_properties(full=True)

    if full:
        page_url = webtools.Url.get_type(url)
        additional = append_properties(page_url)
        all_properties.append({"name" : "Social", "data" : additional})

    return all_properties


def run_cmd_url(url, remote_server):
    output_file = Path("storage") / "out.txt"

    remote_server = remote_server + "/set"

    # TODO timeout

    command = ["poetry", "run", "python", "crawleebeautifulsoup.py", "--url", url, "--remote-server", remote_server]
    
    try:
        # Run the command using subprocess
        result = subprocess.run(
            command,
            #shell=True,
            text=True,
            capture_output=True,
            check=True
        )

        output = result.stdout
        error = result.stderr
        return jsonify({
            "success": True,
            "output": output,
            "error": error
        })
    except subprocess.CalledProcessError as e:
        # Handle command errors
        return jsonify({
            "success": False,
            "output": e.stdout,
            "error": e.stderr,
            "return_code": e.returncode
        })
    except Exception as e:
        # Handle general errors
        return jsonify({
            "success": False,
            "error": str(e)
        })


@app.route('/')
def home():
    text = """
    <h1>Available commands</h1>
    <div><a href="/info">Info</a></div>
    <div><a href="/infoj">Info JSON</a></div>
    <div><a href="/history">History</a></div>
    <div><a href="/historyj">History JSON</a></div>
    <div><a href="/run">Crawl</a></div>
    <div><a href="/social">Social</a></div>
    """

    return get_html(text, index=True)


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

    return get_html(text)


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



@app.route('/history')
def history():
    text = ""

    text += "<h1>History</h1>"

    if len(url_history) == 0:
        text += "<div>No history yet!</div>"
    else:
        for datetime, url, all_properties in reversed(url_history):
            text += "<h2>{} {}</h2>".format(datetime, url)

            contents = all_properties[1]["data"]["Contents"]

            if len(all_properties) > 2:
                status_code = all_properties[3]["data"]["status_code"]
                charset = all_properties[3]["data"]["Charset"]
                content_length = all_properties[3]["data"]["Content-Length"]
                content_type = all_properties[3]["data"]["Content-Type"]

                text += "<div>Status code:{} charset:{} Content-Type:{} Content-Length:{}</div>".format(status_code, charset, content_type, content_length)
            else:
                text += "<div>Data unavailable</div>".format(status_code, charset, content_type, content_length)
            # text += "<div>{}</div>".format(html.escape(str(all_properties)))

    return get_html(text)


@app.route('/historyj')
def historyj():
    json_history = []

    if len(url_history) == 0:
        return json_history

    for datetime, url, all_properties in reversed(url_history):
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

    url_history.append( (datetime.now(), url, all_properties) )

    return jsonify({"success": True, "received": contents})


@app.route('/find', methods=['GET'])
def find_request():
    url = request.args.get('url')

    all_properties = find_response(url)

    if not all_properties:
        return jsonify({
            "success": False,
            "error": "No properties found"
        }), 400

    return jsonify(all_properties)


def append_properties(handler):
    json_obj = {}

    if type(handler) == webtools.Url.youtube_video_handler:
        code = handler.get_video_code()
        h = webtools.ReturnDislike(code)
        json_obj["thumbs_up"] = h.get_thumbs_up()
        json_obj["thumbs_down"] = h.get_thumbs_down()
        json_obj["view_count"] = h.get_view_count()
        json_obj["rating"] = h.get_rating()
        json_obj["upvote_ratio"] = h.get_upvote_ratio()
        json_obj["upvote_view_ratio"] = h.get_upvote_view_ratio()

    elif type(handler) == webtools.HtmlPage:
        reddit = webtools.RedditUrlHandler(handler.url)
        github = webtools.GitHubUrlHandler(handler.url)

        if reddit.is_handled_by():
            handler_data = reddit.get_json_data()
            if handler_data and "thumbs_up" in handler_data:
                json_obj["thumbs_up"] = handler_data["thumbs_up"]
            if handler_data and "thumbs_down" in handler_data:
                json_obj["thumbs_down"] = handler_data["thumbs_down"]
            if handler_data and "upvote_ratio" in handler_data:
                json_obj["upvote_ratio"] = handler_data["upvote_ratio"]
            if handler_data and "upvote_view_ratio" in handler_data:
                json_obj["upvote_view_ratio"] = handler_data["upvote_view_ratio"]

        elif github.is_handled_by():
            handler_data = github.get_json_data()
            if handler_data and "thumbs_up" in handler_data:
                json_obj["thumbs_up"] = handler_data["thumbs_up"]
            if handler_data and "thumbs_down" in handler_data:
                json_obj["thumbs_down"] = handler_data["thumbs_down"]
            if handler_data and "upvote_ratio" in handler_data:
                json_obj["upvote_ratio"] = handler_data["upvote_ratio"]
            if handler_data and "upvote_view_ratio" in handler_data:
                json_obj["upvote_view_ratio"] = handler_data["upvote_view_ratio"]

    return json_obj


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


@app.route('/run', methods=['GET'])
def run_command():
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

    print("Running:{}, with:{}".format(url, crawler_data))

    all_properties = run_webtools_url(url, crawler_data)
    #all_properties = None
    #run_cmd_url(url, remote_server)

    if all_properties:
        if len(url_history) > history_length:
            url_history.pop(0)

        url_history.append( (datetime.now(), url, all_properties) )
    else:
        all_properties = find_response(url)

        if not all_properties:
            return jsonify({
                "success": False,
                "error": "No properties found"
            }), 400

    return jsonify(all_properties)


@app.route('/headers', methods=['GET'])
def run_headers():
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

    all_properties = run_webtools_url(url, crawler_data)
    #all_properties = None
    #run_cmd_url(url, remote_server)

    if all_properties:
        if len(url_history) > history_length:
            url_history.pop(0)

        url_history.append( (datetime.now(), url, all_properties) )
    else:
        all_properties = find_response(url)

        if not all_properties:
            return jsonify({
                "success": False,
                "error": "No properties found"
            }), 400

    return jsonify(all_properties)


@app.route('/social', methods=['GET'])
def get_social():
    url = request.args.get('url')

    if not url:
        return jsonify({
            "success": False,
            "error": "No url provided"
        }), 400

    page_url = webtools.Url.get_type(url)
    additional = append_properties(page_url)

    return jsonify(additional)



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
            "-l", "--history-length", default=200, type=int, help="Length of history"
        )
        self.parser.add_argument("--host", default="0.0.0.0", help="Host")

        self.args = self.parser.parse_args()


if __name__ == '__main__':
    p = CommandLineParser()
    p.parse()

    history_length = p.args.history_length

    app.run(debug=True, host=p.args.host, port=p.args.port, threaded=True)
