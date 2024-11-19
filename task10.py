import datetime
import functools
import time

import redis

redis_client = redis.Redis(host="localhost", port=6379, db=0)


def single(max_processing_time: datetime.timedelta):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            lock = redis_client.lock(
                f"lock:{func.__name__}",
                timeout=int(max_processing_time.total_seconds()),
            )
            if lock.acquire(blocking=False):
                try:
                    return func(*args, **kwargs)
                finally:
                    lock.release()
            else:
                raise RuntimeError("Already running the {func.__name__} function")

        return wrapper

    return decorator
