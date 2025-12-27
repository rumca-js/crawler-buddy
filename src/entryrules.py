"""
Provide mechanism for URL rules:
  - some URLs require special handling, crawler
  - we may want to block certain domains
"""
from pathlib import Path
import json


class EntryRules(object):
    """
    Entry rules
    """
    def __init__(self):
        """ Constructor """
        self.entry_rules = None

        path = Path("entry_rules.json")
        if path.exists():
            with path.open("r") as file:
                self.entry_rules = json.load(file)

    def is_blocked_by_rules(self, url) -> bool:
        """
        Returns indication if URL is blocked by a rule
        """
        if not self.entry_rules:
            return False

        if "entryrules" not in self.entry_rules:
            return False

        for rule in self.entry_rules["entryrules"]:
            if self.is_url_hit(rule, url):
                return True

        return False

    def is_url_hit(self, rule, url) -> bool:
        """
        Returns indication if rule is applied to, connected with URL.
        """
        url_string = rule["rule_url"]

        rule_urls = self.get_rule_urls(url_string)

        for rule_url_string in rule_urls:
            if url.find(rule_url_string) >= 0:
                return True

    def get_rule_urls(self, rule_url):
        """
        Returns URLs used by the rule
        """
        result = set()

        urls = rule_url.split(",")
        for url in urls:
            if url.strip() != "":
                result.add(url.strip())

        return result

    def get_browser(self, url) -> str | None:
        """
        Returns browser specified by rules for URL.
        Returns unique name of crawler_name
        """
        if not self.entry_rules:
            return

        if "entryrules" not in self.entry_rules:
            return

        for rule in self.entry_rules["entryrules"]:
            if self.is_url_hit(rule, url) and rule["browser"]:
                return rule["browser"]
