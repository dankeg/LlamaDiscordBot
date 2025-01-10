import redis
import time

redis_cli = redis.Redis(host="redis", port=6379, charset="utf-8", decode_responses=True)

# Set your key
redis_cli.set("my-first-key", "code-always")

# Get the value of inserted key
print(redis_cli.get("my-first-key"))


def push(*values):
    redis_cli.rpush("QUEUE", *values)


def pull():
    while True:
        msg = redis_cli.rpop("QUEUE")
        print(msg)
        if msg is None:
            time.sleep(0.1)
            continue


push(*[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 34, 12, 12])

pull()
pull()
pull()
