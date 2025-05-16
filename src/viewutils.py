from utils import PermanentLogger
from src import CrawlHistory
from src import webtools


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


def level2color(level):
    if level == "WARNING":
        return "yellow"
    elif level == "ERROR":
        return "red"
    elif level == "NOTIFY":
        return "blue"
    return ""


def status2color(status_code):
    if status_code >= 200 and status_code < 300:
        return "green"
    elif status_code == 403:
        return "yellow"
    elif status_code == 0:
        return ""
    return "red"


def get_entry_html(id, index, url, timestamp, all_properties):
    text = ""

    if not id:
        id = ""
    find_link = "/findj?id={}&index={}".format(id, str(index))
    remove_link = "/removej?id={}&index={}".format(id, str(index))

    timestamp_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")

    text += """<a href="{}"><h2 style="margin-bottom:0px">[{}] {}</h2></a> <a href="{}">Remove</a>\n""".format(
        find_link, timestamp_str, url, remove_link
    )

    response = CrawlHistory.read_properties_section("Response", all_properties)
    options = CrawlHistory.read_properties_section("Settings", all_properties)
    if response:
        status_code = response["status_code"]
        # TODO maybe create a better API
        status_code_text = webtools.status_code_to_text(status_code)

        charset = response["Charset"]
        content_length = response["Content-Length"]
        content_type = response["Content-Type"]

        if options and "name" in options:
            crawler_name = options["name"]
        else:
            crawler_name = ""
        if options and "crawler" in options:
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

    color = status2color(status_code)

    text += "<div>"
    text += f'<span style="color:{color}">Status code:{status_code_text}</span> '
    text += f"charset:{charset} "
    text += f"Content-Type:{content_type} "
    text += f"Content-Length:{content_length} "
    text += f"Crawler name:{crawler_name} "
    text += f"Crawler:{crawler_crawler} "
    text += "</div>\n"

    return text


def rssify(all_properties):
    properties = CrawlHistory.read_properties_section("Properties", all_properties)
    entries = CrawlHistory.read_properties_section("Entries", all_properties)

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
