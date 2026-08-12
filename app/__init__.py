# 1. Standard Library
import time

# 2. Third-party
from flask_limit import RateLimiter
from flask import Flask, Response, g

# 3. Local/Internal
from configs import Config
from app.core.git_automation import main
from app.utils.check_limit import limit
from app.database import db


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)
    limiter = RateLimiter(app)

    @app.before_request
    @limiter.rate_limit
    def load_time_collection_data():
        g.limit_data = (
            db.time_limit.find_one(
                {"username": Config.GITHUB_USERNAME},
                {"_id": 0, "time_last_update": 1, "debug": 1},
            )
            or {}
        )

    @app.route("/")
    @limiter.rate_limit
    def home():

        status, mes = limit.check(time.time())

        if status:
            return main.main()
        return Response(
            f"Skipped: Rate limit active ({mes}s left)",
            mimetype="text/plain",
            status=200,
        )

    return app


__all__ = ["create_app"]
