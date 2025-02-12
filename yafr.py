"""
This is example script about how to use this project as a simple RSS reader
"""

from src.webtools import (
    WebConfig,
    HttpPageHandler,
    FeedClientParser,
    FeedClient,
    ScrapingClient,
)
from sqlalchemy import (
    create_engine,
)


def main():
    WebConfig.init()

    parser = FeedClientParser()
    parser.parse()

    engine = create_engine("sqlite:///feedclient.db")

    p = FeedClient(day_limit=7, engine=engine, parser=parser)

    if p.parser.args.verbose:
        WebConfig.use_print_logging()

    p.run()


if __name__ == "__main__":
    main()
