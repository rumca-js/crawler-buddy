import os
import argparse
import requests

from flask import (
   Flask,
   render_template_string,
   jsonify,
   request,
)
from webtoolkit import (
   RemoteUrl,
   response_to_json,
   request_to_json,
   PageRequestObject,
   HTTP_STATUS_CODE_SERVER_TOO_MANY_REQUESTS,
   HTTP_STATUS_CODE_SERVER_DATA_NOT_READY,
)

from src.crawlercontaineralchemy import CrawlerContainerAlchemy
from src.crawlercontainer import CrawlerContainer
from src.configuration import Configuration
from src.crawlerdata import CrawlerData
from src.views import (
    get_select_widget,
    get_entry_html,
    get_crawl_data,
    level2color,
    rssify,
    get_html,
)


"""
TODO duplicated
"""
def display_history(history_items):
    text = ""
    for crawl_data in reversed(history_items):
        crawl_type = crawl_data.crawl_type
        if crawl_type == CrawlerContainer.CRAWL_TYPE_GET:
            all_properties = crawl_data.data
            entry_text = get_entry_html("", crawl_data)
            text += entry_text
        else:
            text += get_crawl_data("", crawl_data)

    return text


"""
TODO duplicated
"""
def get_requests(server_request):
    url = server_request.args.get("url")
    crawler_name = server_request.args.get("crawler_name")
    if crawler_name == "None":
        crawler_name = None
    if crawler_name == "":
        crawler_name = None
    handler_name = server_request.args.get("handler_name")
    if handler_name == "None":
        handler_name = None
    if handler_name == "":
        handler_name = None
    crawl_id = server_request.args.get("crawl_id")
    if crawl_id == "None":
        crawl_id = None
    if crawl_id == "":
        crawl_id = None

    request = PageRequestObject(url)
    request.crawler_name = crawler_name
    request.handler_name = handler_name

    if crawl_id:
        request.settings["crawl_id"] = crawl_id

    return request


app  = Flask(__name__)
REMOTE_LOCATION=os.environ.get("REMOTE_LOCATION", "")

DEFAULT_HOST="127.0.0.1"
DEFAULT_PORT=3000

if not REMOTE_LOCATION:
    REMOTE_LOCATION = f"http://{DEFAULT_HOST}:{DEFAULT_PORT}"


"""
TODO move elsewhere
"""
class CacheCommandLineParser(object):
    """
    Headers can only be passed by input binary file
    """

    def parse(self):
        global REMOTE_LOCATION

        self.parser = argparse.ArgumentParser(description="Remote server options")

        self.parser.add_argument(
            "--host",
            default=False,
            help="host",
        )

        self.parser.add_argument(
            "--port",
            default=False,
            help="port",
        )

        self.parser.add_argument(
            "--max-rows",
            default=10000,
            help="max rows",
        )

        self.args = self.parser.parse_args()

        if self.args.host and self.args.port:
            REMOTE_LOCATION = f"http://{self.args.host}:{self.args.port}"
        elif self.args.host:
            REMOTE_LOCATION = f"http://{self.args.host}:{DEFAULT_PORT}"
        elif self.args.port:
            REMOTE_LOCATION = f"http://{DEFAULT_HOST}:{self.args.port}"
        else:
            REMOTE_LOCATION = f"http://{DEFAULT_HOST}:{DEFAULT_PORT}"


configuration = Configuration()
parser = CacheCommandLineParser()
parser.parse()


# TODO define 1 day
container = CrawlerContainerAlchemy(records_size=parser.args.max_rows)


@app.route("/")
def index():
    size = container.get_size()

    text = f"""
    Size {size}
    """

    return render_template_string(text)


@app.route("/info")
def info():
    size = container.get_size()

    text = f"""
    Size {size}
    """

    return render_template_string(text)


@app.route("/api/clear")
def api_clear():
    container.clear()
    size = container.get_size()

    text = f"""
    Size {size}
    """

    return render_template_string(text)


@app.route("/api/ping")
def api_ping():
    with requests.get(url=REMOTE_LOCATION, timeout=60, verify=False) as result:
        if result.status_code != 200:
            return jsonify({"status": False})

    # TODO check also if ping to internet works.

    return jsonify({"status": True})


@app.route("/api/get")
def api_get():
    data = CrawlerData(configuration=configuration)
    data.set_request(request)
    page_request = data.get_request_data()

    #page_request = PageRequestObject(url=link)

    all_properties = None

    row = container.get(request=page_request)
    if row:
        time_diff = row.get_time_diff()
        if time_diff.total_seconds() < 3600:
            all_properties = row.data

    if not all_properties:
        remote_url = RemoteUrl(url=page_request.url, remote_server_location=REMOTE_LOCATION)
        response = remote_url.get_response()

        while response and response.get_status_code() == HTTP_STATUS_CODE_SERVER_DATA_NOT_READY:
            response = remote_url.get_response()

        all_properties = remote_url.get_all_properties()
        if all_properties:
            container.add(request=page_request, data=all_properties)

    return jsonify(all_properties)


@app.route("/api/social")
def api_social():
    data = CrawlerData(configuration=configuration)
    data.set_request(request)
    page_request = data.get_request_data()

    #page_request = PageRequestObject(url=link)

    all_properties = None

    row = container.get(request=page_request)
    if row:
        time_diff = row.get_time_diff()
        if time_diff.total_seconds() < 3600:
            all_properties = row.data

    if not all_properties:
        remote_url = RemoteUrl(url=page_request.url, remote_server_location=REMOTE_LOCATION)
        response = remote_url.get_response()

        while response and response.get_status_code() == HTTP_STATUS_CODE_SERVER_DATA_NOT_READY:
            response = remote_url.get_response()

        all_properties = remote_url.get_social_properties()
        if all_properties:
            container.add(request=page_request, data=all_properties)

    return jsonify(all_properties)


@app.route("/api/find")
def api_find():
    page_request = get_requests(request)

    crawl_id = request.args.get("index")
    if crawl_id == "None":
        crawl_id = None
    if crawl_id == "":
        crawl_id = None

    if crawl_id:
        try:
            crawl_id = int(crawl_id)
        except Exception as E:
            pass

    crawler_data = container.get(
        crawl_id=crawl_id, request=page_request,
    )

    if not crawler_data:
        return jsonify({"success": False, "error": f"No properties found {crawl_id} {page_request}"}), 400

    index = crawler_data.crawl_id
    timestamp = crawler_data.timestamp
    all_properties = crawler_data.data

    if not all_properties:
        return jsonify({"success": False, "error": "No properties found"}), 400

    return jsonify(all_properties)


@app.route("/history")
def history():
    text = ""

    text += "<h1>History</h1>\n"

    history_items = container.get_ready_items()

    if len(history_items) == 0:
        text += "<div>No history yet!</div>"
    else:
        text += '<h2><a href="/history?clear=1">Clear all</a></h2>'
        text += display_history(history_items)
    return get_html(id=id, body=text, title="History")


# TODO something to remove db


app.run("0.0.0.0", 3001)
