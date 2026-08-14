# 1. Local/Internal
from configs import Config
from .logger import logger

# 2. Third-party
from flask import g

__all__ = ["limit"]


class CheckLimit:
    def __init__(self) -> None:
        self.debug_active = None

    def check(self, now: float | int, /) -> tuple[bool, int]:

        time_res_db = g.limit_data

        last_update: int = time_res_db.get("time_last_update", 0)
        time_elapsed: float | int = now - last_update

        self.debug_active: bool = time_res_db.get("debug", False)

        logger.debug(f"{last_update} ||| {time_elapsed} ||| {now}")

        if time_elapsed < Config.TIME_LIMIT and not (self.debug_active or Config.DEBUG):
            time_left: int = int(round(Config.TIME_LIMIT - time_elapsed, 0))

            logger.debug(f"Time left: {time_left}")

            return False, time_left

        return True, 0


limit = CheckLimit()
