from app.database import db
from app.utils.logger import logger

import time
import functools

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

