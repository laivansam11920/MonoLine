from app.database import db
from app.utils.logger import logger
from configs import Config

import time
import functools

from flask import g

class Database:

    @staticmethod
    def del_document(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                one_week_ago = time.time() - (7 * 24 * 60 * 60)
                db.ai_res.delete_many({
                    "time": {"$lt": one_week_ago}
                })
            except Exception as e:
                logger.error(e)

            return func(*args, **kwargs)
        return wrapper

    @staticmethod
    def load_time_collection_data(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                g.limit_data = (
                        db.time_limit.find_one(
                            {"username": Config.GITHUB_USERNAME},
                            {"_id": 0, "time_last_update": 1, "debug": 1},
                        )
                        or {}
                )
            except Exception as e:
                logger.error(e)
                g.limit_data = {}

            return func(*args, **kwargs)
        return wrapper
