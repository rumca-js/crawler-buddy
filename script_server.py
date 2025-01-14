"""
Starts flask server at the specified location.

Access through:
    ip:port/run?url=.... etc.

Examples:
http://127.0.0.1:3000/run?url=https://google.com&crawler_data={"crawler":"StealthRequestsCrawler","name":"StealthRequestsCrawler","settings": {"timeout_s":20}}
http://127.0.0.1:3000/run?url=https://google.com&crawler_data={"crawler":"SeleniumChromeFull","name":"SeleniumChromeFull","settings": {"timeout_s":50, "driver_executable" : "/usr/bin/chromedriver"}}
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


url_history = []   # contains tuples
history_length = 200


def find_response(input_url):
    for datetime, url, all_properties, crawler_data in reversed(url_history):
        if input_url == url and all_properties:
            return all_properties


def run_webtools_url(url, crawler_data):
    page_url = webtools.Url(url)
    options = page_url.get_init_page_options()

    if crawler_data:
        if "crawler" in crawler_data:
            crawler_data["crawler"] = webtools.WebConfig.get_crawler_from_string(crawler_data["crawler"])
            options.mode_mapping = [crawler_data]

    page_url = webtools.Url(url, page_options=options)
    response = page_url.get_response()
    all_properties = page_url.get_properties(full=True)

    return all_properties


def run_cmd_url(url, remote_server):
    output_file = Path("storage") / "out.txt"

    remote_server = remote_server + "/set"

    command = ["poetry", "run", "python", "crawleebeautifulsoup.py", "--url", url, "--remote-server", remote_server]
    
    try:
        result = subprocess.run(
            command,
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
        return jsonify({
            "success": False,
            "output": e.stdout,
            "error": e.stderr,
            "return_code": e.returncode
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        })


@app.route('/')
def home():
    text = """
    <h1>Run Command</h1>
    <form action="/run" method="get">
        Command: <input type="text" name="url" required>
        <button type="submit">Run</button>
    </form>
    """

    if len(url_history) == 0:
        return text

    text += "<h1>Url history</h1>"
    for datetime, url, all_properties, crawler_data in reversed(url_history):
        text += "<h2>{} {}</h2>".format(datetime, url)

        contents = all_properties[1]["data"]["Contents"]

        status_code = all_properties[3]["data"]["status_code"]
        charset = all_properties[3]["data"]["Charset"]
        content_length = all_properties[3]["data"]["Content-Length"]
        content_type = all_properties[3]["data"]["Content-Type"]

        text += "<div>Status code:{} charset:{} Content-Type:{} Content-Length{}</div>".format(status_code, charset, content_type, content_length)
        # text += "<div>{}</div>".format(html.escape(str(all_properties)))

    return text


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
    all_properties.append({"name" : "Resonse", "data" : response})

    if len(url_history) > history_length:
        url_history.pop(0)

    url_history.append( (datetime.now(), url, all_properties, None) )

    return jsonify({"success": True, "received": contents})


@app.route('/run', methods=['GET'])
def run_command():
    # Retrieve the command from the query parameters
    url = request.args.get('url')
    crawler_data = request.args.get('crawler_data')

    if not url:
        return jsonify({
            "success": False,
            "error": "No url provided"
        }), 400

    parsed_crawler_data = None
    if crawler_data:
        try:
            parsed_crawler_data = json.loads(crawler_data)
        except json.JSONDecodeError as E:
            print(str(E))

    if parsed_crawler_data is None:
        parsed_crawler_data = {}

    if "settings" not in parsed_crawler_data:
        parsed_crawler_data["settings"] = {}

    remote_server = f"http://{request.host}"

    parsed_crawler_data["settings"]["remote_server"] = remote_server

    print("Running:{}, with:{} at:{}".format(url, crawler_data, remote_server))

    all_properties = run_webtools_url(url, parsed_crawler_data)
    # all_properties = None
    # run_cmd_url(url, remote_server)

    if all_properties:
        if len(url_history) > history_length:
            url_history.pop(0)

        url_history.append( (datetime.now(), url, all_properties, crawler_data) )
    else:
        all_properties = find_response(url)

        if not all_properties:
            return jsonify({
                "success": False,
                "error": "No properties found"
            }), 400

    return jsonify(all_properties)



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
