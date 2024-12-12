from pathlib import Path

from ..basictypes import fix_path_for_os
from rsshistory.webtools import Url, YouTubeVideoHandler, InputContent


def fix_entry_link_name(link):
    link = link.replace("\\", "")
    link = link.replace("/", "")
    link = fix_path_for_os(link)
    if len(link) > 150:
        link = link[:150]
    link = link.replace(".", "")
    link = link.replace("-", "")
    return link + ".html"


def get_youtube_style():
    return """
.youtube_player_container {
    position: relative;
    width: 50%;
    padding-bottom: 26.25%;
    /* background-color: yellow; */
}
.youtube_player_frame {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    border: 0;
}
    """


class HtmlEntryExporter(object):
    def __init__(self, output_directory, entry, index_file=None, verbose=False):
        self.entry = entry
        self.output_directory = output_directory
        self.index_file = index_file
        self.verbose = verbose

    def write(self):
        text = self.get_entry_text()

        file_name = self.get_entry_file_name()
        if self.verbose:
            print("Writing:{}".format(file_name))

        try:
            with open(file_name, "w", encoding="utf-8") as fh:
                fh.write(text)
        except OSError as E:
            print(
                "Cannot write file:{} len:{}\n{}".format(
                    str(file_name), len(str(file_name)), str(E)
                )
            )

    def get_entry_text(self):
        entry = self.entry

        # index.html entry text
        id = entry.id
        thumbnail = entry.thumbnail
        title = entry.title
        link = entry.link
        description = entry.description
        date_published = entry.date_published
        source = entry.source
        # source_title = entry.source

        show_thumbnail = True

        if thumbnail and description and description.find(thumbnail) >= 0:
            show_thumbnail = False

        if not thumbnail:
            show_thumbnail = False

        index_file = "index.html"

        if self.index_file:
            index_file = self.index_file.get_file_name()

        text = ""
        text = "<!DOCTYPE html>"
        text += "<html>"
        text += "<head>"
        text += "   <meta>"
        text += "     <title>{}</title>".format(entry.title)
        text += "   </meta>"
        text += "   <style>"
        text += get_youtube_style()
        text += "   </style>"
        text += "</head>"
        text += "<body>"
        text += f'<a href="{index_file}"><h2>Index</h2></a>'
        text += f'<a href="{link}">'

        if show_thumbnail:
            text += self.get_preview()

        if description:
            c = InputContent(description)
            description = c.htmlify()

        text += f"<h1>[{id}] {title}</h1>"
        text += f"</a>"
        text += f"<div>{source}</div>"
        text += f"<div>{date_published}</div>"
        text += f"<div><pre>{description}</pre></div>"
        text += "</body>"
        text += "</html>"
        return text

    def get_preview(self):
        url = Url(self.entry.link)
        handler = url.get_handler()

        if type(handler) is Url.youtube_video_handler:
            h = YouTubeVideoHandler(url=self.entry.link)
            return '<div class="youtube_player_container"><iframe src="{0}" frameborder="0" allowfullscreen class="youtube_player_frame" referrerpolicy="no-referrer-when-downgrade"></iframe></div>'.format(
                h.get_link_embed()
            )
        else:
            thumbnail = self.entry.thumbnail
            return (
                f'<div><img style="width:400px;height=300px" src="{thumbnail}" /></div>'
            )

    def get_entry_file_name(self):
        link = self.entry.link
        return self.output_directory / fix_entry_link_name(link)


class HtmlIndexExporter(object):
    def __init__(
        self,
        cwd=Path("."),
        output_file="index.html",
        previous_index=None,
        verbose=False,
    ):
        self.verbose = verbose
        self.output_file = output_file
        self.output_directory = cwd
        self.previous_index = previous_index

        self.text = "<!DOCTYPE html>"
        self.text += "<html>"
        self.text += "<head>"
        self.text += "  <meta>"
        self.text += "    <title>{}</title>".format(output_file)
        self.text += "  </meta>"
        self.text += "  <style>"
        self.text += get_youtube_style()
        self.text += "  </style>"
        self.text += "</head>"
        self.text += "<body>"

        if self.previous_index:
            previous_file = self.previous_index.get_file_name()
            self.text += f'<a href="{previous_file}"><h2>Previous Page</h2></a>'

        self.text += "<ul>"

    def add_entry(self, entry):
        # index.html entry text
        thumbnail = entry.thumbnail
        title = entry.title
        link = entry.link
        description = entry.description
        date_published = entry.date_published
        source = entry.source
        # source_title = entry.source

        entry_file_name = self.get_entry_file_name(entry)

        self.text += f'<a href="{entry_file_name}">'
        if thumbnail:
            self.text += (
                f'<div><img style="width:400px;height=300px" src="{thumbnail}" /></div>'
            )

        self.text += f"<h1>{title}</h1>"
        self.text += f"</a>"
        self.text += f"<div>{source}</div>"
        self.text += f"<div>{date_published}</div>"
        self.text += f"<hr/>"

    def write(self, next_index=None):
        if self.previous_index:
            previous_file = self.previous_index.get_file_name()
            self.text += f'<a href="{previous_file}"><h2>Previous Page</h2></a>'

        if next_index:
            next_file = next_index.get_file_name()
            self.text += f'<a href="{next_file}"><h2>Next Page</h2></a>'

        self.text += "</ul>"
        self.text += "</body>"
        self.text += "</html>"

        with open(
            str(self.output_directory / self.output_file), "w", encoding="utf-8"
        ) as fh:
            fh.write(self.text)

    def get_file_name(self):
        return self.output_file

    def get_entry_file_name(self, entry):
        return fix_entry_link_name(entry.link)


class HtmlExporter(object):
    def __init__(self, output_directory, entries, verbose=False):
        self.output_directory = output_directory
        self.entries = entries
        self.current_index = None
        self.verbose = verbose

    def write(self):
        index_number = 0

        self.current_index = HtmlIndexExporter(
            cwd=self.output_directory,
            output_file=self.get_index_file_name(index_number),
            verbose=self.verbose,
        )

        for row_index, entry in enumerate(self.entries):
            if row_index % 100 == 99:
                index_number += 1
                next_index = HtmlIndexExporter(
                    cwd=self.output_directory,
                    output_file=self.get_index_file_name(index_number),
                    previous_index=self.current_index,
                    verbose=self.verbose,
                )

                self.current_index.write(next_index)

                self.current_index = next_index

            self.write_entry_file(entry)
            self.current_index.add_entry(entry)

        self.current_index.write()

    def write_entry_file(self, entry):
        # write entry file
        w = HtmlEntryExporter(
            self.output_directory, entry, self.current_index, verbose=self.verbose
        )
        w.write()

    def get_index_file_name(self, index_number):
        if index_number == 0:
            return "index.html"
        else:
            return f"index_{index_number}.html"
