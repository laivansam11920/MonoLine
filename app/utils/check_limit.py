from configs import Config

from flask import g, Response
import time
from functools import wraps

__all__ = ["Limit"]


class Limit:

    @staticmethod
    def check_limit(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            is_allowed, time_left = Limit.check(time.time())

            if not is_allowed:
                return Response(
                    f"Skipped: Rate limit active ({time_left}s left)",
                    mimetype="text/plain",
                    status=200,
                )

            return func(*args, **kwargs)

        return wrapper

    @staticmethod
    def check(now: float | int) -> tuple:

        time_res_db = g.limit_data

        last_update: int = time_res_db.get("time_last_update", 0)
        time_elapsed: float | int = now - last_update

        debug_active: bool = time_res_db.get("debug", False)

        if debug_active or Config.DEBUG:
            return True, time_elapsed

        if time_elapsed < Config.TIME_LIMIT:
            time_left: int = int(round(Config.TIME_LIMIT - time_elapsed, 0))
            return False, time_left

        return True, 0
