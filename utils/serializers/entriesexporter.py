import logging

from utils.converters import (
    PageSystem,
    ModelCollectionConverter,
    JsonConverter,
    MarkDownConverter,
)


class EntriesExporter(object):
    """
    Generic exporter that just puts entries to file
    """

    def __init__(self, handle, entries, page_dir):
        self._entries = entries
        self.handle = handle

    def export(self):
        if self._entries.count() == 0:
            return

        cc = ModelCollectionConverter(self._entries)
        items = cc.get_map_full()

        js_converter = JsonConverter(items)
        js_converter.set_export_columns(LinkDataController.get_all_export_names())

        self.handle.write_text(js_converter.export())

        md = MarkDownConverter(items, self.md_template_link)
        md_text = md.export()

        """
        sources = SourceDataController.objects.filter(url=source_url)

        if sources.exists():
            from .converters import MarkDownSourceConverter

            msc = MarkDownSourceConverter(sources[0], self.source_template)
            msc_text = msc.export()
            md_text = msc_text + "\n\n" + md_text
        """

        self.handle.write_text(md_text)


class EntriesPageExporter(object):
    """
    Paged format
    """

    def __init__(self, entries, export_directory):
        self.export_directory = export_directory
        self.entries = entries
        self.current_handle = None
        self.current_page_no = None

    def get_pagination(self):
        return 1000

    def export(self):
        # TODO remove hardcoded value?
        page_system = PageSystem(entries.count(), self.get_pagination())

        for page in range(page_system.no_pages):
            slice_limits = page_system.get_slice_limits(page)

            sliced_entries = entries[slice_limits[0] : slice_limits[1]]

            self.export_sliced(page, sliced_entries)

    def close(self):
        if self.current_handle:
            self.current_handle.close()

    def export_sliced(self, page, entries):
        page_dir = self.get_page_dir(page)
        inner_serializer = EntriesExporter(self.get_file_handle(), entries, page_dir)
        inner_serializer.export(sources)

    def get_file_dir(self, page_no):
        return (
            self.export_dir / Path("entries") / "{page_no:05d}".format(page_no=page_no)
        )

    def get_file_name(self, page_no):
        page_dir = self.get_file_dir(page_no)
        return page_dir / "entries.md"

    def get_file_handle(self, page_no):
        if self.current_page_no is None and self.current_page_no != page_no:
            if self.current_handle:
                self.current_handle.close()

            self.current_handle = open(self.get_file_name(page_no), "w")

        return self.current_handle


class EntriesDateExporter(object):
    """
    Writes entries for source
    """

    def __init__(self, directory, day_iso):
        self.directory = directory
        self.day_iso = day_iso

    def write(self, source_url):
        from ..controllers import LinkDataController
        from .entriesexporter import EntriesExporter

        date_range = DateUtils.get_range4day(day_iso)
        entries = LinkDataController.objects.filter(
            source=self.source_url, date_published__range=date_range
        )

        ex = EntriesExporter(entries)
        ex.export_entries(self.source_url, clean_url, input_path)

    def write_all_sources(self):
        """
        We do not want to provide for each day cumulative view. Users may want to select which 'streams' are selected individually '
        """
        from ..controllers import SourceDataController, LinkDataController

        date_range = DateUtils.get_range4day(day_iso)

        # some entries might not have source in the database - added manually.
        # first capture entries, then check if has export to CMS.
        # if entry does not have source, it was added manually and is subject for export

        entries = LinkDataController.objects.filter(date_published__range=date_range)
        sources_urls = set(entries.values_list("source", flat=True).distinct())

        for source_url in sources_urls:
            source_objs = SourceDataController.objects.filter(url=source_url)
            if source_objs.exists() and not source_objs[0].export_to_cms:
                continue

            self.write_for_day(input_path, day_iso)


class YearlyExporter(object):
    def __init__(self, config, username=""):
        self.username = username

    def get_ordered_queryset(input_queryset):
        return input_queryset.order_by("date_published", "link")

    def get_start_year(self):
        """
        We export from oldest entries
        """
        entries = BookmarksExporter.get_ordered_queryset(
            LinkDataController.objects.all()
        )
        if len(entries) > 0:
            entry = entries[0]
            if entry.date_published:
                str_date = entry.date_published.strftime("%Y")
                try:
                    return int(str_date)
                except ValueError as E:
                    LinkDatabase.info("Error: {}".format(str(E)))

        return self.get_current_year()

    def get_current_year(self):
        today = DateUtils.get_date_today()
        year = int(DateUtils.get_datetime_year(today))
        return year

    def export(self, directory):
        entries_dir = directory

        if entries_dir.exists():
            shutil.rmtree(entries_dir)

        for year in range(self.get_start_year(), self.get_current_year() + 1):
            LinkDatabase.info("Writing bookmarks for a year {}".format(year))

            all_entries = self.get_entries(year)

            # do not differenciate export on language.
            # some entries could have not language at all, or some other foreign languages
            converter = BookmarksEntryExporter(self._cfg, all_entries)
            converter.export("bookmarks", entries_dir / str(year))

    def get_entries(self, year):
        start_date = datetime.date(year, 1, 1)
        stop_date = datetime.date(year + 1, 1, 1)

        therange = (start_date, stop_date)

        result_entries = []

        user = self.get_user()

        if user:
            bookmarks = UserBookmarks.get_user_bookmarks(user)
            # this returns IDs, not 'objects'
            result_entries = bookmarks.values_list("entry_object", flat=True)
            result_entries = LinkDataController.objects.filter(id__in=result_entries)
            result_entries = result_entries.filter(date_published__range=therange)
        else:
            result_entries = LinkDataController.objects.filter(
                bookmarked=True, date_published__range=therange
            )

        result_entries = BookmarksExporter.get_ordered_queryset(result_entries)

        return result_entries

    def get_user(self):
        users = User.objects.filter(username=self.username)
        if users.count() > 0:
            return users[0]
