from flask import Flask, Response
from configs import Config
from app.core.git_automation import main
from app.database import db
from time import time

def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)

    @app.route("/")
    def home():
        now = time()

        time_res_db = db.time_limit.find_one({"username": Config.DB_NAME}, {"_id": 0, "time_last_update": 1, "debug": 1}) or {}
        last_update: int = time_res_db.get("time_last_update", 0)
        time_elapsed: float | int = now - last_update
        debug_active: bool = time_res_db.get("debug", False)

        if time_elapsed < Config.TIME_LIMIT and not (debug_active or Config.DEBUG):
            time_left: int = int(round(Config.TIME_LIMIT - time_elapsed, 0))

            return Response(
                f"Skipped: Rate limit active ({time_left}s left)",
                mimetype="text/plain",
                status=200,
            )

        return main.main()

    return app
