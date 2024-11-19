import redis

import json


class RedisQueue:
    def __init__(self, client):
        self.client = client
        self.queue_name = "task_queue"

    def publish(self, msg: dict):
        self.client.rpush(self.queue_name, json.dumps(msg))

    def consume(self) -> dict:
        msg = self.client.lpop(self.queue_name)
        if msg:
            return json.loads(msg)
        return None


if __name__ == "__main__":
    client = redis.StrictRedis(host="localhost", port=6379, db=0)
    q = RedisQueue(client)
    q.publish({"a": 1})
    q.publish({"b": 2})
    q.publish({"c": 3})

    assert q.consume() == {"a": 1}
    assert q.consume() == {"b": 2}
    assert q.consume() == {"c": 3}
