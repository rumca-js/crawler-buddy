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
   PageRequestObject
)

from src.crawlercontaineralchemy import CrawlerContainerAlchemy

app  = Flask(__name__)

# TODO define 1 day
container = CrawlerContainerAlchemy()

@app.route("/info")
def info():
    size = container.get_size()

    text = f"""
    Size {size}
    """

    return render_template_string(text)

@app.route("/clear")
def index():
    container.clear()
    size = container.get_size()

    text = f"""
    Size {size}
    """

    return render_template_string(text)

@app.route("/crawl")
def crawl():
    link = request.args.get("link")
    page_request = PageRequestObject(url=link)

    row = container.get(request=page_request)
    if row:
        all_properties = row.data
    else:
        remote_server_location = "http://127.0.0.1:3000"
        remote_url = RemoteUrl(url=link, remote_server_location=remote_server_location)
        response = remote_url.get_response()

        all_properties = remote_url.get_all_properties()
        container.add(request=page_request, data=all_properties)

    return jsonify(all_properties)

# TODO something to remove db

app.run("0.0.0.0", 3001)
