import random
import time


class RateLimitExceed(Exception):
    pass


import redis


class RateLimiter:
    def __init__(self, client: redis.Redis):
        self.client = client

    def test(self) -> bool:
        current_time = float(time.time())
        self.client.zremrangebyscore("requests", "-inf", current_time - 3)
        if self.client.zcard("requests") < 5:
            self.client.zadd("requests", {current_time: current_time})
            return True
        return False


def make_api_request(rate_limiter: RateLimiter):
    if not rate_limiter.test():
        raise RateLimitExceed
    else:
        # какая-то бизнес логика
        pass


if __name__ == "__main__":
    import redis

    rate_limiter = RateLimiter(redis.Redis(host="localhost", port=6379, db=0))

    for _ in range(50):
        time.sleep(random.random() / 5)

        try:
            make_api_request(rate_limiter)
        except RateLimitExceed:
            print("Rate limit exceed!")
        else:
            print("All good")
