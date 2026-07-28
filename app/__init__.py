from flask import Flask
from configs import Config
from app.core.git_automation import main


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)

    @app.route("/")
    def home():
        return main.main() #

    return app
