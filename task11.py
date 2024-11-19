import redis

import ast


class RedisQueue:
    def __init__(self):
        self.client = redis.StrictRedis(host="localhost", port=6379, db=0)
        self.queue_name = "task_queue"

    def publish(self, msg: dict):
        self.client.rpush(self.queue_name, repr(msg))

    def consume(self) -> dict:
        msg = self.client.lpop(self.queue_name)
        if msg:
            return ast.literal_eval(msg.decode())
        return None


if __name__ == "__main__":
    q = RedisQueue()
    q.publish({"a": 1})
    q.publish({"b": 2})
    q.publish({"c": 3})

    assert q.consume() == {"a": 1}
    assert q.consume() == {"b": 2}
    assert q.consume() == {"c": 3}
