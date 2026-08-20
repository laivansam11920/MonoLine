from flask_limit import RateLimiter
from flask import Flask, Response

from configs import Config
from app.core.git_automation import git_services
from app.utils.check_limit import Limit
from app.database import db
from app.utils.logger import logger
from app.database import Database

__all__ = ["create_app"]


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)
    limiter = RateLimiter(app)

    @app.route("/")
    @limiter.rate_limit
    @Database.load_time_collection_data
    @Limit.check_limit
    @Database.del_document
    def home() -> Response:
        return git_services.main()

    return app
