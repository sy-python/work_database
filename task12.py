import random
import time


class RateLimitExceed(Exception):
    pass


class RateLimiter:
    def __init__(self):
        self.request_times = []

    def test(self) -> bool:
        current_time = time.time()
        # Remove requests that are older than 3 seconds
        self.request_times = [t for t in self.request_times if current_time - t < 3]
        # Check if there are less than 5 requests in the last 3 seconds
        if len(self.request_times) < 5:
            self.request_times.append(current_time)
            return True
        return False


def make_api_request(rate_limiter: RateLimiter):
    if not rate_limiter.test():
        raise RateLimitExceed
    else:
        # какая-то бизнес логика
        pass


if __name__ == "__main__":
    rate_limiter = RateLimiter()

    for _ in range(50):
        time.sleep(random.random())

        try:
            make_api_request(rate_limiter)
        except RateLimitExceed:
            print("Rate limit exceed!")
        else:
            print("All good")
