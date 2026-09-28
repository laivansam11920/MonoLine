from flask import Flask

from configs import Config

__all__ = ["create_app"]


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)

    @app.route("/ping")
    def ping():
        print("pong", flush=True)
        return {"ping": "pong"}

    return app
