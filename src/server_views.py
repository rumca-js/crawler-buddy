from pathlib import Path
from flask import (
    Blueprint,
    request,
    jsonify,
    Response,
    current_app
)
import html
import base64
from datetime import datetime

from webtoolkit import (
    HttpPageHandler,
    WebLogger,
    RemoteUrl,
    RemoteServer,
    PageRequestObject,
    PageResponseObject,
    ContentLinkParser,
    DomainCache,
    HTTP_STATUS_CODE_CONNECTION_ERROR,
)
from src import webtools
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


views = Blueprint('views', __name__)


def get_crawlers():
    result = [""]

    config = current_app.config['configuration'].get_crawler_config()
    for item in config:
        name = item["crawler_name"]
        result.append(name)

    return result


def get_handlers():
    handlers = [""]
    request_obj = PageRequestObject("")
    for handler in Url(url="", request=request_obj).get_handlers():
        handlers.append(handler.__name__)

    return handlers


def get_crawler_text():
    text = ""

    config = current_app.config['configuration'].get_crawler_config()
    for item in config:
        name = item["crawler_name"]
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


@views.route("/")
def index():
    id = request.args.get("id")
    if not current_app.config['configuration'].is_allowed(id):
        return get_html(id=id, body="Cannot access this view", title="Error")

    if not id:
        id = ""

    # fmt: off

    command_links = []
    command_links.append({"link" : "/info", "name":"Info", "description":"shows configuration"})
    command_links.append({"link" : "/system", "name":"System monitoring", "description":"system monitoring"})
    command_links.append({"link" : "/about", "name":"About", "description":"About"})

    operational_links = []
    operational_links.append({"link" : "/get", "name":"Get", "description":"get web page crawl information"})
    operational_links.append({"link" : "/ping", "name":"Ping", "description":"get ping result"})
    operational_links.append({"link" : "/link", "name":"Link", "description":"get link formats, canonical, etc."})
    operational_links.append({"link" : "/feeds", "name":"Feeds", "description":"get link feeds"})
    operational_links.append({"link" : "/scanlinks", "name":"Scan links", "description":"scan for links"})
    operational_links.append({"link" : "/scandomains", "name":"Scan domains", "description":"scan for domains"})
    operational_links.append({"link" : "/social", "name":"Social data", "description":"get social data"})
    operational_links.append({"link" : "/contents", "name":"Contents form", "description":"get web page contents"})
    operational_links.append({"link" : "/rssify", "name":"RSSify", "description":"get RSS for link"})

    mgmt_links = []
    mgmt_links.append({"link" : "/history", "name":"History", "description":"crawl history"})
    mgmt_links.append({"link" : "/queue", "name":"Queue", "description":"queue"})
    mgmt_links.append({"link" : "/find", "name":"Find", "description":"find response"})
    mgmt_links.append({"link" : "/debug", "name":"Debug", "description":"debug information"})

    api_links = []
    api_links.append({"link" : "/getj", "name":"Get", "description":"Crawl data: page text, status"})
    api_links.append({"link" : "/socialj", "name":"Social data", "description":"Social data, likes, dislikes"})
    api_links.append({"link" : "/linkj", "name":"Links", "description":"link information"})
    api_links.append({"link" : "/archivesj", "name":"Archive links", "description":"links to archives, digital libraries"})
    api_links.append({"link" : "/feedsj", "name":"Feeds", "description":"feeds information"})
    api_links.append({"link" : "/pingj", "name":"Ping", "description":"Ping response"})
    api_links.append({"link" : "/scanlinksj", "name":"Scan links", "description":"links scan"})
    api_links.append({"link" : "/scandomainsj", "name":"Scan domains", "description":"Links domain scan"})
    api_links.append({"link" : "/contentsr", "name":"Contents response", "description":"returns page contents, as if read by a browser"})
    api_links.append({"link" : "/rssifyr", "name":"RSSifyr", "description":"returns information, readable by feed clients"})
    api_links.append({"link" : "/findj", "name":"Find in history", "description":"returns information about history entry"})
    api_links.append({"link" : "/historyj", "name":"History", "description":"History"})
    api_links.append({"link" : "/clearj", "name":"Clear history", "description":"remove all history entries"})
    api_links.append({"link" : "/removej", "name":"Remove history", "description":"remove one history entry"})
    api_links.append({"link" : "/infoj", "name":"Info", "description":"Crawling capabilities information"})

    # fmt: on

    text = ""

    text += """<h1>System</h1>"""

    for link_data in command_links:
        link = link_data["link"]
        name = link_data["name"]
        description = link_data["description"]

        text += f"""<div><a href="{link}?id={id}">{name}</a> - {description}</div>"""

    text += "<h2>Management</h2>"

    for link_data in mgmt_links:
        link = link_data["link"]
        name = link_data["name"]
        description = link_data["description"]

        text += f"""<div><a href="{link}?id={id}">{name}</a> - {description}</div>"""

    text += "<h2>Forms</h2>"

    for link_data in operational_links:
        link = link_data["link"]
        name = link_data["name"]
        description = link_data["description"]

        text += f"""<div><a href="{link}?id={id}">{name}</a> - {description}</div>"""

    text += "<h2>API</h2>"

    for link_data in api_links:
        link = link_data["link"]
        name = link_data["name"]
        description = link_data["description"]

        text += f"""<div><a href="{link}?id={id}">{name}</a> - {description}</div>"""

    version = current_app.config['configuration'].__version__

    text += """<p>"""
    text += f"""Version:{version}"""
    text += """</p>"""

    return get_html(id=id, body=text, title="Crawler Buddy", index=True)


@views.route("/info")
def info():
    id = request.args.get("id")
    if not current_app.config['configuration'].is_allowed(id):
        return get_html(id=id, body="Cannot access this view", title="Error")

    text = """
    <h1>Crawlers</h1>
    """

    text += get_crawler_text()

    text += "<h2>Configuration</h2>"
    for key, value in current_app.config['configuration'].data.items():
        text += "<div>{}:{}</div>".format(key, value)

    text += "<h2>System</h2>"
    size = current_app.config['crawler_main'].container.get_size()
    records_size = current_app.config['crawler_main'].container.records_size
    time_span = current_app.config['crawler_main'].container.time_cache_m
    text += "<div>{}:{}</div>".format("History size", size)
    text += "<div>{}:{}</div>".format("Records size", records_size)
    text += "<div>{}:{}</div>".format("Time cache [m]", time_span)

    text += "<h2>System</h2>"
    domain_length = 0
    domain_max_length = 0
    if DomainCache.object:
        domain_length = DomainCache.object.get_length()
    if DomainCache.object:
        domain_max_length = DomainCache.object.get_max_length()
    text += f"<div>Domain_length {domain_length}/{domain_max_length}</div>"

    runner = current_app.config["task_runner"]
    threads_size = runner.get_size()
    running_ids_len = len(runner.running_ids)
    text += f"<div>Processing Thread: {runner.is_thread_ok()}</div>"
    text += f"<div>Running IDS: {running_ids_len}</div>"
    text += f"<div>Running futures: {runner.get_size()}</div>"

    process_count = webtools.WebConfig.count_chrom_processes()
    text += "<div>{}:{}</div>".format("Chrome processes", process_count)
    text += "<div>{}:{}</div>".format("Selenium count", webtools.SeleniumDriver.counter)

    chromedriver_path = Path("/usr/bin/chromedriver")
    if chromedriver_path.exists():
        text += "<div>Chromedriver at {} exists".format(chromedriver_path)
    else:
        text += "<div>Chromedriver at {} does not exist".format(chromedriver_path)

    return get_html(id=id, body=text, title="Configuration")


@views.route("/infoj")
def infoj():
    id = request.args.get("id")
    if not current_app.config['configuration'].is_allowed(id):
        return get_html(id=id, body="Cannot access this view", title="Error")

    text = """
    <h1>Crawlers</h1>
    """

    all = {}
    crawlers = []
    properties = {}

    config = current_app.config['configuration'].get_crawler_config()
    for item in config:
        crawlers.append(item)

    for aproperty, value in current_app.config['configuration'].data.items():
        properties[str(aproperty)] = str(value)

    all["crawlers"] = crawlers
    all["properties"] = properties

    return jsonify(all)


@views.route("/history")
def history():
    id = request.args.get("id")
    if not current_app.config['configuration'].is_allowed(id):
        return get_html(id=id, body="Cannot access this view", title="Error")

    clear_all = request.args.get("clear")
    if clear_all:
        current_app.config['crawler_main'].container.clear()

    text = ""

    text += "<h1>History</h1>\n"

    history_items = current_app.config['crawler_main'].container.get_ready_items()

    if len(history_items) == 0:
        text += "<div>No history yet!</div>"
    else:
        text += '<h2><a href="/history?clear=1">Clear all</a></h2>'
        text += display_history(history_items)
    return get_html(id=id, body=text, title="History")


@views.route("/historyj")
def historyj():
    id = request.args.get("id")
    if not current_app.config['configuration'].is_allowed(id):
        return get_html(id=id, body="Cannot access this view", title="Error")

    json_history = []

    if current_app.config['crawler_main'].container.get_size() == 0:
        return json_history

    for crawl_data in reversed(current_app.config['crawler_main'].container.get_ready_items()):
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


@views.route("/debug")
def debug():
    id = request.args.get("id")
    if not current_app.config['configuration'].is_allowed(id):
        return get_html(id=id, body="Cannot access this view", title="Error")

    if not current_app.config['configuration'].is_set("debug"):
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


@views.route("/set", methods=["POST"])
def set_response():
    data = request.json
    if not data or "Contents" not in data:
        return jsonify({"success": False, "error": "Missing 'Contents'"}), 400

    u = set_response_impl(request)

    p = u.handler.get_page_handler()

    all_properties = u.get_properties(full=True)

    current_app.config['crawler_main'].container.add(crawl_type=CrawlerContainer.CRAWL_TYPE_GET, url=url, data=all_properties)

    return jsonify({"success": True, "received": contents})


def set_response_impl(request):
    # id = request.args.get("id")
    # if not current_app.config['configuration'].is_allowed(id):
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


@views.route("/find", methods=["GET"])
def find():
    id = request.args.get("id")
    if not current_app.config['configuration'].is_allowed(id):
        return get_html(id=id, body="Cannot access this view", title="Error")

    url = request.args.get("url")
    crawler_name = request.args.get("crawler_name")
    handler_name = request.args.get("handler_name")

    if not url and not crawler_name:
        form_html = get_crawling_form("Find", "/findj", id)

        return get_html(id=id, body=form_html, title="Find")
    else:
        crawler_data = current_app.config['crawler_main'].container.get(
            url=url, crawler_name=name,
        )

        if not crawler_data:
            return get_html(
                id=id, body="Cannot find any entry matching data", title="Find"
            )

        index = crawler_data.crawl_id 
        timestamp = crawler_data.timestamp 
        all_properties = crawler_data.data 

        entry_text = get_entry_html(id, crawl_data)

        return get_html(id=id, body=entry_text, title=url)


@views.route("/findj", methods=["GET"])
def findj():
    id = request.args.get("id")
    if not current_app.config['configuration'].is_allowed(id):
        return get_html(id=id, body="Cannot access this view", title="Error")

    url = request.args.get("url")
    name = request.args.get("crawler_name")
    index = request.args.get("index")

    if index:
        index = int(index)

    crawler_data = current_app.config['crawler_main'].container.get(
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


@views.route("/removej", methods=["GET"])
def removej():
    id = request.args.get("id")
    if not current_app.config['configuration'].is_allowed(id):
        return get_html(id=id, body="Cannot access this view", title="Error")

    index = request.args.get("index")

    if index:
        index = int(index)

    if current_app.config['crawler_main'].container.remove(crawl_id=index):
        return jsonify({"success": True})

    return jsonify({"success": False, "error": "Could not remove"}), 400


@views.route("/clearj", methods=["GET"])
def clearj():
    id = request.args.get("id")
    if not current_app.config['configuration'].is_allowed(id):
        return get_html(id=id, body="Cannot access this view", title="Error")

    current_app.config['crawler_main'].container.clear()
    return jsonify({"success": True})


@views.route("/get", methods=["GET"])
def get():
    id = request.args.get("id")
    if not current_app.config['configuration'].is_allowed(id):
        return get_html(id=id, body="Cannot access this view", title="Error")

    form_text = get_crawling_form("Get JSON information", "/getj", id)

    return get_html(id=id, body=form_text, title="Get")


@views.route("/getj", methods=["GET"])
def getj():
    id = request.args.get("id")
    if not current_app.config['configuration'].is_allowed(id):
        return get_html(id=id, body="Cannot access this view", title="Error")

    all_properties = current_app.config['crawler_main'].get_all_properties(request)
    if not all_properties:
        return (
            jsonify(
                {
                    "success": False,
                    "error": "Cannot obtain properties for request {}".format(str(request)),
                }
            ),
            400,
        )

    return jsonify(all_properties)


@views.route("/rssify", methods=["GET"])
def rssify_this():
    id = request.args.get("id")
    if not current_app.config['configuration'].is_allowed(id):
        return get_html(id=id, body="Cannot access this view", title="Error")

    form_text = get_crawling_form("Get RSS for link", "/rssifyr", id)

    return get_html(id=id, body=form_text, title="Get")


@views.route("/rssifyr", methods=["GET"])
def rssifyr():
    id = request.args.get("id")
    if not current_app.config['configuration'].is_allowed(id):
        return get_html(id=id, body="Cannot access this view", title="Error")

    url = request.args.get("url")

    if not url:
        return jsonify({"success": False, "error": "No url provided"}), 400

    all_properties = current_app.config['crawler_main'].get_all_properties(request)
    if all_properties:
        properties = CrawlerHistory.read_properties_section(
            "Properties", all_properties
        )
        entries = CrawlerHistory.read_properties_section("Entries", all_properties)

        if not entries or len(entries) == 0:
            if "feeds" in properties:
                for feed in properties["feeds"]:
                    all_properties = current_app.config['crawler_main'].get_crawl_properties(
                        feed, crawler_data
                    )
                    if all_properties:
                        break

    return Response(rssify(all_properties), mimetype="application/rss+xml")


@views.route("/contents", methods=["GET"])
def contents():
    id = request.args.get("id")
    if not current_app.config['configuration'].is_allowed(id):
        return get_html(id=id, body="Cannot access this view", title="Error")

    form_text = get_crawling_form("Get link contents", "/contentsr", id)

    return get_html(id=id, body=form_text, title="Get")


@views.route("/contentsr", methods=["GET"])
def contentsr():
    id = request.args.get("id")
    if not current_app.config['configuration'].is_allowed(id):
        return get_html(id=id, body="Cannot access this view", title="Error")

    url = request.args.get("url")

    if not url:
        return jsonify({"success": False, "error": "No url provided"}), 400

    all_properties = current_app.config['crawler_main'].get_all_properties(request)

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


@views.route("/scanlinks", methods=["GET"])
def scanlinks():
    id = request.args.get("id")
    if not current_app.config['configuration'].is_allowed(id):
        return get_html(id=id, body="Cannot access this view", title="Error")

    form_text = get_crawling_form("Scan for links", "/scanlinksj", id)

    return get_html(id=id, body=form_text, title="Get")


@views.route("/scanlinksj", methods=["GET"])
def scanlinksj():
    id = request.args.get("id")
    if not current_app.config['configuration'].is_allowed(id):
        return get_html(id=id, body="Cannot access this view", title="Error")

    url = request.args.get("url")

    if not url:
        return jsonify({"success": False, "error": "No url provided"}), 400

    all_properties = current_app.config['crawler_main'].get_all_properties(request)

    if not all_properties:
        return jsonify({"success": False, "error": "No properties found"}), 400

    page_url = RemoteUrl(url=url, all_properties=all_properties)

    response = page_url.get_response()

    if response:
        parser = ContentLinkParser(url, response.get_text())

        return jsonify({"success": True, "links": list(parser.get_links())})
    return jsonify({"success": False, "error": "No response for link"}), 400


@views.route("/scandomains", methods=["GET"])
def scandomains():
    id = request.args.get("id")
    if not current_app.config['configuration'].is_allowed(id):
        return get_html(id=id, body="Cannot access this view", title="Error")

    form_text = get_crawling_form("Scan for domains", "/scandomainsj", id)

    return get_html(id=id, body=form_text, title="Get")


@views.route("/scandomainsj", methods=["GET"])
def scandomainsj():
    id = request.args.get("id")
    if not current_app.config['configuration'].is_allowed(id):
        return get_html(id=id, body="Cannot access this view", title="Error")

    url = request.args.get("url")

    if not url:
        return jsonify({"success": False, "error": "No url provided"}), 400

    all_properties = current_app.config['crawler_main'].get_all_properties(request)

    if not all_properties:
        return jsonify({"success": False, "error": "No properties found"}), 400

    page_url = RemoteUrl(url=url, all_properties=all_properties)

    response = page_url.get_response()

    if response:
        parser = ContentLinkParser(url, response.get_text())

        return jsonify({"success": True, "links": list(parser.get_domains())})
    return jsonify({"success": False, "error": "No response for link"}), 400


@views.route("/headers", methods=["GET"])
def headers():
    # TODO implement
    id = request.args.get("id")
    if not current_app.config['configuration'].is_allowed(id):
        return get_html(id=id, body="Cannot access this view", title="Error")

    url = request.args.get("url")

    if not url:
        return jsonify({"success": False, "error": "No url provided"}), 400

    all_properties = current_app.config['crawler_main'].get_all_properties(request, headers=True)

    return jsonify(all_properties)


@views.route("/social", methods=["GET"])
def social():
    id = request.args.get("id")
    if not current_app.config['configuration'].is_allowed(id):
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


@views.route("/socialj", methods=["GET"])
def socialj():
    """
    Dynamic, social data.
    Thumbs up, etc.
    """
    id = request.args.get("id")
    if not current_app.config['configuration'].is_allowed(id):
        return get_html(id=id, body="Cannot access this view", title="Error")

    url = request.args.get("url")

    if not url:
        return jsonify({"success": False, "error": "No url provided"}), 400

    properties = current_app.config['crawler_main'].get_social_properties(request, url)

    if properties:
        return jsonify(properties)
    else:
        return jsonify({})


@views.route("/ping", methods=["GET"])
def ping():
    id = request.args.get("id")
    if not current_app.config['configuration'].is_allowed(id):
        return get_html(id=id, body="Cannot access this view", title="Error")

    url = request.args.get("url")

    if not url:
        form_html = get_link_form("Find ping information", "pingj", id)
        return get_html(id=id, body=form_html, title="Social")

    page_url = webtools.Url(url)

    text = "<h1>Ping</h1>"

    text += str(url.ping())

    return get_html(id=id, body=text, title="Social")


@views.route("/pingj", methods=["GET"])
def pingj():
    """
    Dynamic, social data.
    Thumbs up, etc.
    """
    id = request.args.get("id")
    if not current_app.config['configuration'].is_allowed(id):
        return get_html(id=id, body="Cannot access this view", title="Error")

    url = request.args.get("url")
    if url:
        page_url = webtools.Url(url)
        response = page_url.ping()

        if response.is_valid():
            return jsonify({"status": True})

        if response.status_code == HTTP_STATUS_CODE_CONNECTION_ERROR:
            return jsonify({"status": False})

    all_properties = current_app.config['crawler_main'].get_all_properties(request, ping=True)
    response = RemoteServer.read_properties_section("Response", all_properties)

    if response:
        status_code = response["status_code"]
        is_valid = response["is_valid"]
        return jsonify({"status": is_valid})

    return jsonify({"status": False})


@views.route("/linkj", methods=["GET"])
def linkj():
    id = request.args.get("id")
    if not current_app.config['configuration'].is_allowed(id):
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


@views.route("/link", methods=["GET"])
def link():
    id = request.args.get("id")
    if not current_app.config['configuration'].is_allowed(id):
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


@views.route("/feedsj", methods=["GET"])
def feedsj():
    id = request.args.get("id")
    if not current_app.config['configuration'].is_allowed(id):
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


@views.route("/feeds", methods=["GET"])
def feeds():
    id = request.args.get("id")
    if not current_app.config['configuration'].is_allowed(id):
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


@views.route("/archivesj", methods=["GET"])
def archivesj():
    id = request.args.get("id")
    if not current_app.config['configuration'].is_allowed(id):
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


def display_queue(queue_items):
    text = ""
    for crawl_data in queue_items:
        html_data = get_entry_html("",  crawl_data)
        text += html_data

        crawl_id = crawl_data.crawl_id

        running_text = "No"
        task_runner = current_app.config.get('task_runner')
        if task_runner:
            if task_runner.is_running(crawl_id):
                running_text = "Yes"

        text += f'<div>Running: {running_text}</div>\n'

    return text


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


@views.route("/queue", methods=["GET"])
def queue():
    id = request.args.get("id")
    if not current_app.config['configuration'].is_allowed(id):
        return get_html(id=id, body="Cannot access this view", title="Error")

    size = current_app.config['crawler_main'].container.get_size()

    text = ""

    text += "<h1>Queue</h1>\n"

    items = current_app.config['crawler_main'].container.get_queued_items()

    if len(items) == 0:
        text += "<div>Nothing in queue yet!</div>"
    else:
        text += display_queue(items)

    return get_html(id=id, body=text, title="Queue")


@views.route("/about", methods=["GET"])
def about():
    id = request.args.get("id")
    if not current_app.config['configuration'].is_allowed(id):
        return get_html(id=id, body="Cannot access this view", title="Error")

    text = """
    <h2>About</h2>
    <div>
    Crawler buddy is a program that allows to obtain Internet pages contents,
    </div>

    <ul>
      <li>Allows to automate the process.</li>
      <li>Provides multiple ways how the internet pages are obtained</li>
      <li>To automate API endpoints need to be used</li>
    </ul>

    <div>
    For details please see <a href="https://github.com/rumca-js/crawler-buddy">GitHub readme</a>
    </div>
    """

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


@views.route("/system", methods=["GET"])
def system():
    id = request.args.get("id")
    if not current_app.config['configuration'].is_allowed(id):
        return get_html(id=id, body="Cannot access this view", title="Error")

    if not current_app.config['configuration'].is_set("debug"):
        return get_html(id=id, body="Cannot access this view", title="Error")

    text = "<h1>System monitoring</h1>\n"

    # Assuming get_hardware_info and get_process_info are moved or imported correctly
    # For now, let's assume they are available in the context
    from utils.systemmonitoring import get_hardware_info, get_process_info
    info = get_hardware_info()
    info["processes"] = get_process_info()

    text = dict_to_html(info)

    return get_html(id=id, body=text, title="Processes")
