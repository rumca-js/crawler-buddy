import argparse

class CommandLineParser(object):
    """
    Headers can only be passed by input binary file
    """

    def parse(self):
        self.parser = argparse.ArgumentParser(description="Remote server options")

        self.parser.add_argument(
            "-l",
            "--history-length",
            default=200,
            type=int,
            help="Length of history",
        )

        self.parser.add_argument(
            "-t",
            "--time-cache-minutes",
            default=10,
            type=int,
            help="Time cache in minutes",
        )

        self.parser.add_argument(
            "-k",
            "--kill-processes",
            default=False,
            help="Kill processes at start",
            action="store_true",
        )

        self.parser.add_argument("--cert-file", help="Host")
        self.parser.add_argument("--cert-key", help="Host")

        self.args = self.parser.parse_args()
