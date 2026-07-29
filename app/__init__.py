from flask import Flask
from configs import Config
from app.core.git_automation import main


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)

    @app.route("/")
    def home():
        res, status = main.main()
        return res.get("msg"), status

    return app
