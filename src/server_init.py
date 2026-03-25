import os
from pathlib import Path
from flask import Flask
from webtoolkit import WebLogger
from utils import PermanentLogger
from src.configuration import Configuration
from src.crawler import Crawler
from src.server_views import views
from src.crawlercontaineralchemy import CrawlerContainerAlchemy
from src.crawlercontainer import CrawlerContainer


BASE_DIR = Path(__file__).resolve().parent.parent


def create_app():
    app = Flask(__name__,
        static_folder=os.path.join(BASE_DIR, "static"),
        static_url_path="/static",
    )

    # Initialize components
    WebLogger.web_logger = PermanentLogger()
    print("Creating configuration")
    configuration = Configuration()
    task_runner = None

    # Store components in app config
    app.config['configuration'] = configuration
    app.config['task_runner'] = task_runner

    if configuration.is_db_history_container():
        print("Creating DB container")
        app.config['container'] = CrawlerContainerAlchemy()
    else:
        print("Creating RAM container")
        app.config['container'] = CrawlerContainer()

    print("Creating crawler")
    app.config['crawler_main'] = Crawler(container=app.config['container'])
    
    # Register blueprints
    app.register_blueprint(views)

    return app
