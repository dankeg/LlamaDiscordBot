import time
import redis
import json
from llamaai.model.Generation import LlamaModel

redis_cli = redis.Redis(host="redis", port=6379, charset="utf-8", decode_responses=True)


def push_response(*values: str) -> None:
    """Pushes model response to redis RESPONSE queue."""
    redis_cli.rpush("RESPONSE", *values)


def pull_query() -> str:
    """Pulls a query from the redis queue QUERY.

    Returns:
        str: Model query popped from the queue
    """
    msg = redis_cli.rpop("QUERY")
    return msg


def handle_queries():
    """Primary Runner Loop, handling new queries, generating responses, and passing back results."""
    while True:
        msg = pull_query()
        if msg is not None:
            msg = json.loads(msg)
            message = msg["message"]
            message_id = msg["message_id"]
            channel_id = msg["channel_id"]
            user_id = msg["user_id"]

            message = LlamaModel.query_model(message)
            push_response(
                json.dumps(
                    {
                        "message": message,
                        "message_id": message_id,
                        "channel_id": channel_id,
                        "user_id": user_id,
                    }
                )
            )
        else:
            time.sleep(0.1)
