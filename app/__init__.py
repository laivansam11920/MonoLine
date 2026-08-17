# 1. Third-party
from flask_limit import RateLimiter
from flask import Flask, Response, g

# 2. Local/Internal
from configs import Config
from app.core.git_automation import git_services
from app.utils.check_limit import limit
from app.database import db
from app.utils.logger import logger

# 3. Standard Library
import time

__all__ = ["create_app"]


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)
    limiter = RateLimiter(app)

    @app.before_request
    @limiter.rate_limit
    def load_time_collection_data() -> None:

        g.limit_data = (
            db.time_limit.find_one(
                {"username": Config.GITHUB_USERNAME},
                {"_id": 0, "time_last_update": 1, "debug": 1},
            )
            or {}
        )

    @app.route("/")
    @limiter.rate_limit
    def home() -> Response:

        status, mes = limit.check(now=time.time())

        if status:
            return git_services.main()
        return Response(
            f"Skipped: Rate limit active ({mes}s left)",
            mimetype="text/plain",
            status=200,
        )

    return app
