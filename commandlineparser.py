import argparse

class CommandLineParser(object):
    """
    Headers can only be passed by input binary file
    """

    def parse(self):
        self.parser = argparse.ArgumentParser(description="Remote server options")

        self.parser.add_argument(
            "-k",
            "--kill-processes",
            default=False,
            help="Kill processes at start",
            action="store_true",
        )

        self.parser.add_argument(
            "-m",
            "--multi-process",
            default=False,
            help="Crawling is done in a separate thread",
            action="store_true",
        )

        self.parser.add_argument(
            "-d",
            "--debug",
            help="Debug indication",
            action="store_true",
        )

        self.parser.add_argument("--cert-file", help="Host")
        self.parser.add_argument("--cert-key", help="Host")

        self.args = self.parser.parse_args()
