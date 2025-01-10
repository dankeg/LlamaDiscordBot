from transformers import AutoTokenizer, AutoModelForCausalLM
import time
import redis
import json
from huggingface_hub import login
from llamaai.model.Generation import LlamaModel

redis_cli = redis.Redis(host="redis", port=6379, charset="utf-8", decode_responses=True)


def push_response(*values):
    redis_cli.rpush("RESPONSE", *values)


def pull_query():
    msg = redis_cli.rpop("QUERY")
    return msg


def handle_queries():
    while True:
        msg = pull_query()
        if msg is not None:
            msg = json.loads(msg)
            message = msg["message"]
            message_id = msg["message_id"]
            channel_id = msg["channel_id"]

            message = LlamaModel.query_model(message)
            push_response(
                json.dumps(
                    {
                        "message": message,
                        "message_id": message_id,
                        "channel_id": channel_id,
                    }
                )
            )
        else:
            time.sleep(0.1)
