from flask import Flask, Response
from configs import Config
from app.core.git_automation import main
from app.utils.check_limit import limit
import time


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)

    @app.route("/")
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