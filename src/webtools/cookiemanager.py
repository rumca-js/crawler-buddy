from pathlib import Path
import json
from webtoolkit import UrlLocation, WebLogger


class CookieManager(object):
    def __init__(self):
        pass

    def write(self, link, cookies):
        try:
            location = UrlLocation(link)
            domain_only = location.get_domain_only()
            return self.write_cookies_domain(domain_only, cookies)
        except Exception as E:
            print(str(E))
            WebLogger.exc(E)
        return False

    def read(self, link):
        if not link:
            return

        location = UrlLocation(link)
        domain_only = location.get_domain_only()
        if domain_only.find("youtube.com") >= 0:
            cookies = {}
            cookies["CONSENT"] = "YES+cb.20210328-17-p0.en+F+678"
            return cookies

        return None
        """
        try:
            location = UrlLocation(link)
            domain_only = location.get_domain_only()
            return self.read_cookies_domain(domain_only)
        except Exception as E:
            WebLogger.exc(E)
        return []
        """

    def write_cookies_domain(self, domain_only, cookies):
        data_dir = Path("data")
        data_dir.mkdir(exist_ok=True)

        file_path = data_dir / f"{domain_only}.json"

        with file_path.open("w", encoding="utf-8") as fh:
            json.dump(cookies, fh, indent=4)
            return True

        return False

    def read_cookies_domain(self, domain):
        data_dir = Path("data")
        if not data_dir.exists():
            print("Directory does not exist")
            return []

        file_path = data_dir / f"{domain}.json"
        if not file_path.exists():
            print("File does not exist")
            return []

        with file_path.open("r", encoding="utf-8") as fh:
            cookies = json.load(fh)

        return cookies
