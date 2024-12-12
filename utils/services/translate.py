from rsshistory.webtools import UrlLocation


class TranslatePage(object):
    def __init__(self, url):
        self.url = url

    def get_translate_url(self):
        return self.url


class GoogleTranslate(TranslatePage):
    def __init__(self, url):
        super().__init__(url)

    def get_translate_url(self):
        p = UrlLocation(self.url)
        parts = p.parse_url()
        parts[2] = parts[2].replace("-", "--")
        parts[2] = parts[2].replace(".", "-")

        if parts[0] == "http":
            remainder = (
                "?_x_tr_sch=http&_x_tr_sl=auto&_x_tr_tl=en&_x_tr_hl=en&_x_tr_pto=wapp"
            )
        else:
            remainder = "?_x_tr_sl=auto&_x_tr_tl=en&_x_tr_hl=en&_x_tr_pto=wapp"

        if len(parts) > 4:
            return (
                "https"
                + parts[1]
                + parts[2]
                + ".translate.goog"
                + parts[3]
                + remainder
                + parts[4].replace("?", "&")
            )
        elif len(parts) > 3:
            return (
                "https" + parts[1] + parts[2] + ".translate.goog" + parts[3] + remainder
            )
        elif len(parts) > 2:
            return "https" + parts[1] + parts[2] + ".translate.goog/" + remainder


class TranslateBuilder(object):
    def get(url):
        return GoogleTranslate(url)
