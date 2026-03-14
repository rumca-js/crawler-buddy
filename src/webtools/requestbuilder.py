from src.webtools import WebConfig
from src.entryrules import EntryRules

from .cookiemanager import CookieManager

from webtoolkit import (
    CrawlerInterface,
    PageRequestObject,
)
from ..configuration import Configuration


class RequestBuilder(object):

    def get_default_request(url):
        page_request = PageRequestObject(url)
        page_request = RequestBuilder.update_crawler_name(page_request)
        page_request = RequestBuilder.update_request_ext(page_request)
        return page_request

    def update_request(page_request):
        page_request = RequestBuilder.update_crawler_name(page_request)
        page_request = RequestBuilder.update_request_ext(page_request)
        return page_request

    def update_crawler_name(request):
        if request.crawler_name is not None:
            return request

        browser = EntryRules.get_object().get_browser(request.url)
        if browser:
            request.crawler_name = browser

        if not request.crawler_name:
            configuration = Configuration.get_object()
            browser = configuration.get_default_browser()
            if browser:
                request.crawler_name = browser

        if not request.crawler_name:
            browser = WebConfig.get_default_browser_name()
            if browser:
                request.crawler_name = browser

        return request

    def update_request_ext(request):
        """
        Fills necessary fields within request
        """

        request.crawler_type = None

        """
        script = WebConfig.get_script_from_name(browser)

        # TODO
        page_request.settings["script"] = script
        page_request.settings["remote_server"] = "http://127.0.0.1:3000"
        """

        if request.crawler_name and request.crawler_type is None:
            if request.crawler_type is None:
                configuration = Configuration.get_object()
                mapping_data = configuration.get_browser(request.crawler_name)
                request = RequestBuilder.settings_to_request(request, mapping_data)

            if request.crawler_type is None:
                mapping_data = WebConfig.get_browser(request.crawler_name)
                request = RequestBuilder.settings_to_request(request, mapping_data)

        if request.timeout_s is None or request.timeout_s == 0:
            request.timeout_s = WebConfig.get_default_timeout_s()

        cookie_manager = CookieManager()
        cookies = cookie_manager.read(request.url)
        request.cookies = cookies

        # TODO not really sure if we should use crawler interface here

        """
        interface = CrawlerInterface(request.url)
        headers = interface.get_default_headers()
        request.request_headers = headers
        """

        return request

    def settings_to_request(page_request, crawler_settings):
        if crawler_settings is None:
            return page_request

        if page_request.crawler_type is None:
            crawler_class_name = crawler_settings.get("crawler_class_name")
            if crawler_class_name:
                crawler_class = WebConfig.get_crawler_class_from_string(crawler_class_name)
                page_request.crawler_type = crawler_class(request=page_request)

        if page_request.crawler_type is None:
            crawler_name = crawler_settings.get("crawler_name")
            crawler_class = WebConfig.get_crawler_class_from_crawler_name(crawler_name)
            page_request.crawler_type = crawler_class(request=page_request)

        def set_property_if_none(page_request, setting_name, crawler_settings, key_in_settings):
            if getattr(page_request, setting_name) is None:
                setting_value = crawler_settings.get("settings", {}).get(key_in_settings)
                if setting_value is not None:
                    setattr(page_request, setting_name, setting_value)

        settings = crawler_settings.get("settings", {})
        set_property_if_none(page_request, 'user_agent', settings, 'User-Agent')
        set_property_if_none(page_request, 'request_headers', settings, 'request_headers')
        set_property_if_none(page_request, 'timeout_s', settings, 'timeout_s')
        set_property_if_none(page_request, 'delay_s', settings, 'delay_s')
        set_property_if_none(page_request, 'ssl_verify', settings, 'ssl_verify')
        set_property_if_none(page_request, 'respect_robots', settings, 'respect_robots_txt')
        set_property_if_none(page_request, 'bytes_limit', settings, 'bytes_limit')
        set_property_if_none(page_request, 'accept_types', settings, 'accept_types')

        if "driver_executable" in settings:
            page_request.settings["driver_executable"] = settings["driver_executable"]

        remote_server = settings.get("remote_server")
        if not remote_server:
            # TODO copy from configuraiont
            settings["remote_server"] = "http://127.0.0.1:3000"

        page_request.settings = settings

        return page_request
