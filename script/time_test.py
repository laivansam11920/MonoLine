from time import time
import functools

def time_point(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        s = time()
        res = func(*args, **kwargs)
        e = time()

        return res, f"[{func.__name__}]: {e - s:.4f}"

    return wrapper
