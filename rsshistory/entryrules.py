from pathlib import Path
import json


class EntryRules(object):
    def __init__(self):
        self.entry_rules = None

        path = Path("entry_rules.json")
        if path.exists():
            with path.open("r") as file:
                self.entry_rules = json.load(file)

    def is_blocked_by_rules(self, url):
        if not self.entry_rules:
            return False

        if "entryrules" not in self.entry_rules:
            return False

        for rule in self.entry_rules["entryrules"]:
            if self.is_url_hit(rule, url):
                return True

        return False

    def is_url_hit(self, rule, url):
        url_string = rule["rule_url"]

        rule_urls = self.get_rule_urls(url_string)

        for rule_url_string in rule_urls:
            if url.find(rule_url_string) >= 0:
                return True

    def get_rule_urls(self, rule_url):
        result = set()

        urls = rule_url.split(",")
        for url in urls:
            result.add(url.strip())

        return result

    def get_browser(self, url):
        if not self.entry_rules:
            return False

        if "entryrules" not in self.entry_rules:
            return False

        for rule in self.entry_rules["entryrules"]:
            if self.is_url_hit(rule, url) and rule["browser"]:
                return rule["browser"]
