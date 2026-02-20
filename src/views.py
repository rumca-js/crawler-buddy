from utils import PermanentLogger
from webtoolkit import (
   status_code_to_text,
   is_status_code_valid,
   is_status_code_invalid,
   json_to_request,
   json_to_response,
   RemoteServer,
)
from src import CrawlerContainer


def level2color(level):
    if level == "WARNING":
        return "yellow"
    elif level == "ERROR":
        return "red"
    elif level == "NOTIFY":
        return "blue"
    return ""


def status2color(status_code):
    valid = is_status_code_valid(status_code)
    invalid = is_status_code_invalid(status_code)

    if valid:
        return "green"
    if invalid:
        return "red"
    elif status_code == 0:
        return ""
    else:
        return "orange"


def list_to_options(options_list):
    """
    Generates an HTML form with a select dropdown based on a list of options.

    Parameters:
        options_list (list): A list of strings for the dropdown options.
    Returns:
        str: An HTML string containing the options.
    """
    options_list = [str(item) for item in options_list]

    options_html = "\n".join(f'        <option value="{item}">{item}</option>' for item in options_list)
    return options_html


def get_select_widget(field_name, options_list):
    options_html = list_to_options(options_list)

    select_html = f"""
    <label for="{field_name}">{field_name}</label><br>
    <select type="text" id="{field_name}" name="{field_name}"><br><br>
      {options_html}
    </select>
    """

    return select_html


def get_template(name, context=None):
    with open("static/templates/" + name) as fh:
        data = fh.read()
        if context:
            for item in context:
                value = context[item]
                key = "{" + item + "}"
                if value is None:
                    value = ""
                else:
                    value = str(value)
                data = data.replace(key, value)

        return data


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
        <link rel="stylesheet" href="static/css.css"/>
    </head>
    <body>
    {}
    </body>
    </html>
    """.format(
        title, body
    )

    return html


def get_entry_html(id, crawl_data):
    text = ""

    crawl_type = crawl_data.crawl_type
    url = crawl_data.url
    timestamp = crawl_data.timestamp
    crawl_id = crawl_data.crawl_id
    all_properties = crawl_data.data

    if not id:
        id = ""
    find_link = "/findj?id={}&index={}".format(id, str(crawl_id))
    remove_link = "/removej?id={}&index={}".format(id, str(crawl_id))

    timestamp_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")

    text += f"""<a href="{find_link}"><h2 style="margin-bottom:0px">[{timestamp_str}] {url}</h2>
      </a>
      <a href="{remove_link}">Remove</a>\n
      """

    request = crawl_data.request_real
    response = None
    status_code = 0
    status_code_text = "No status"
    charset = ""
    content_length = ""
    content_type = ""
    crawler_name = ""
    handler_name = ""
    crawl_type_str = CrawlerContainer.crawl_type_to_str(crawl_type)

    if all_properties:
        response_json = RemoteServer.read_properties_section("Response", all_properties)
        response = json_to_response(response_json)


    if response:
        status_code = response.get_status_code()
        # TODO maybe create a better API
        status_code_text = status_code_to_text(status_code)

        charset = response.get_encoding()
        content_length = response.get_content_length()
        content_type = response.get_content_type()

    if request:
        crawler_name = request.crawler_name
        handler_name = request.handler_name

    color = ""
    try:
        color = status2color(status_code)
    except Exception as E:
        color = "Status is string"

    text += "<div>"
    text += f"<div>Crawl Type:{crawl_type_str} Crawl ID:{crawl_id}</div>"
    text += f'<span style="color:{color}">Status code:{status_code_text}</span> '

    if crawl_type == CrawlerContainer.CRAWL_TYPE_GET:
        if charset:
            text += f"charset:{charset} "
        if content_type:
            text += f"Content-Type:{content_type} "
        if content_length:
            text += f"Content-Length:{content_length} "
        if handler_name:
            text += f"Handler name:{handler_name} "
        if crawler_name:
            text += f"Crawler name:{crawler_name} "
        if request is None:
            text += f"Request is not defined "
    else:
        text += f"<div>{all_properties} </div>"
    text += "</div>\n"

    return text


def get_crawl_data(id, crawl_data):
    text = ""

    crawl_type = crawl_data.crawl_type
    url = crawl_data.url
    timestamp = crawl_data.timestamp
    crawl_id = crawl_data.crawl_id

    request = crawl_data.request_real

    find_link = "/findj?id={}&index={}".format(id, str(crawl_id))
    remove_link = "/removej?id={}&index={}".format(id, str(crawl_id))

    crawl_type = CrawlerContainer.crawl_type_to_str(crawl_type)
    crawler_name = ""
    handler_name = ""
    if request:
        crawler_name = request.crawler_name
        handler_name = request.handler_name

    text += f"""
<a href="{find_link}">
   <h2 style="margin-bottom:0px">[{timestamp}] {url}</h2>
</a>
<a href="{remove_link}">Remove</a>
    """

    text += "<div>"
    text += f"<span>Crawl Type:{crawl_type} Crawl ID:{crawl_id}</span>"
    if handler_name:
        text += f"Handler name:{handler_name} "
    if crawler_name:
        text += f"Crawler name:{crawler_name} "
    text += "</div>"

    return text


def rssify(all_properties):
    properties = CrawlerHistory.read_properties_section("Properties", all_properties)
    entries = CrawlerHistory.read_properties_section("Entries", all_properties)

    rss_template = """<?xml version="1.0" encoding="UTF-8"?>
<rss xmlns:dc="http://purl.org/dc/elements/1.1/" 
     xmlns:content="http://purl.org/rss/1.0/modules/content/" 
     xmlns:atom="http://www.w3.org/2005/Atom" 
     version="2.0" 
     xmlns:media="http://search.yahoo.com/mrss/">
    <channel>
        {channel_info}
        {items}
    </channel>
</rss>"""

    channel_info = ""
    if properties.get("title"):
        channel_info += f"<title>{properties['title']}</title>\n"
    if properties.get("link"):
        channel_info += f"<link>{properties['link']}</link>\n"
    if properties.get("description"):
        channel_info += f"<description>{properties['description']}</description>\n"
    if properties.get("thumbnail"):
        channel_info += f"<image><url>{properties['thumbnail']}</url></image>\n"
    if properties.get("author"):
        channel_info += f"<author><name>{properties['author']}</name></author>\n"
    if properties.get("date_published"):
        channel_info += f"<published>{properties['date_published']}</published>\n"
    if properties.get("language"):
        channel_info += f"<language>{properties['language']}</language>\n"

    items = ""
    for entry in entries:
        entry_info = "<item>\n"

        if entry.get("title"):
            entry_info += f"<title><![CDATA[{entry['title']}]]></title>\n"
        if entry.get("link"):
            entry_info += f"<link><![CDATA[{entry['link']}]]></link>\n"
        if entry.get("description"):
            entry_info += (
                f"<description><![CDATA[{entry['description']}]]></description>\n"
            )
        if entry.get("date_published"):
            entry_info += f"<pubDate><![CDATA[{entry['date_published']}]]></pubDate>\n"
        if entry.get("thumbnail"):
            entry_info += f"<media:thumbnail url=\"{entry['thumbnail']}\"/>\n"

        entry_info += "</item>\n"

        items += entry_info

    return rss_template.format(channel_info=channel_info, items=items)
