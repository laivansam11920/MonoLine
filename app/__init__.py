from flask import Flask

from configs import Config
from app.core.git_automation import git_services
from app.database import db
from app.utils.logger import logger
from app.database import Database

__all__ = ["create_app"]


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)

    @app.route("/ping")
    def ping():
        print("pong", flush=True)
        return {"ping": "pong"}

    return app
