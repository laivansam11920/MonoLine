from time import time
import functools
from app.utils.logger import logger

def time_point(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        bat_dau = time()
        ket_qua = func(*args, **kwargs)

        ket_thuc = time()

        return ket_qua, f"[{func.__name__}]: {ket_thuc - bat_dau:.4f}"

    return wrapper