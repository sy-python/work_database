import datetime
import functools
import time

import redis

redis_client = redis.Redis(host="localhost", port=6379, db=0)


def single(max_processing_time: datetime.timedelta):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            key = f"lock:{func.__name__}"
            value = str(time.time())
            timeout = int(max_processing_time.total_seconds())
            if redis_client.set(key, value, nx=True, ex=timeout):
                try:
                    return func(*args, **kwargs)
                finally:
                    redis_client.delete(key)
            else:
                raise RuntimeError("Already running the {func.__name__} function")

        return wrapper

    return decorator
