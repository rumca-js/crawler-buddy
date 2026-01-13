import os
from pathlib import Path
from flask import Flask
from webtoolkit import WebLogger
from utils import PermanentLogger
from src.configuration import Configuration
from src.crawler import Crawler
from src.server_views import views


BASE_DIR = Path(__file__).resolve().parent.parent


def create_app():
    app = Flask(__name__,
        static_folder=os.path.join(BASE_DIR, "static"),
        static_url_path="/static",
    )

    # Initialize components
    WebLogger.web_logger = PermanentLogger()
    configuration = Configuration()
    crawler_main = Crawler()
    task_runner = None

    # Store components in app config
    app.config['configuration'] = configuration
    app.config['crawler_main'] = crawler_main
    app.config['task_runner'] = task_runner
    
    # Register blueprints
    app.register_blueprint(views)

    return app
