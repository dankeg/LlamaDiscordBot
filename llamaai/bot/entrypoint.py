import discord
from discord.ext import tasks
import json
import redis
import time

redis_cli = redis.Redis(host="redis", port=6379, charset="utf-8", decode_responses=True)

# Set your key
redis_cli.set("my-first-key", "code-always")

# Get the value of inserted key
print(redis_cli.get("my-first-key"))


def push_query(*values):
    redis_cli.rpush("QUERY", *values)


def pull_response(count=10):
    contents = []
    for _ in range(count):
        msg = redis_cli.rpop("RESPONSE")
        if msg is None:
            time.sleep(0.1)
            continue
        else:
            contents.append(msg)
    return contents


intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

token_file = open("license.txt", "r")
DISCORD_TOKEN = token_file.read()

opted_in_users = set()


def load_opted_in_users():
    global opted_in_users
    try:
        with open("opted_in_users.txt", "r") as f:
            opted_in_users = set(line.strip() for line in f)
    except FileNotFoundError:
        opted_in_users = set()


def save_opted_in_users():
    with open("opted_in_users.txt", "w") as f:
        for user_id in opted_in_users:
            f.write(f"{user_id}\n")


async def send_long_message(channel, message, chunk_size=1900):
    for i in range(0, len(message), chunk_size):
        chunk = message[i : i + chunk_size]
        await channel.send(chunk)


def read_conversation_history(user_id):
    file_path = f"{user_id}_conversation.json"
    try:
        with open(file_path, "r") as file:
            conversation_history = json.load(file)
    except FileNotFoundError:
        conversation_history = []
    return conversation_history


def write_conversation_history(user_id, conversation_history):
    file_path = f"{user_id}_conversation.json"
    with open(file_path, "w") as file:
        json.dump(conversation_history, file)


@client.event
async def on_ready():
    print(f"Logged in as {client.user}")
    load_opted_in_users()
    print(f"Loaded opted-in users: {opted_in_users}")
    updater.start()

    await client.change_presence(activity=discord.Game(name="Use !help for info!"))


@tasks.loop(seconds=5)  # Run this task every 5 seconds
async def updater():
    responses = pull_response()
    for response in responses:
        model_response = json.loads(response)
        message = model_response["message"]
        message_id = model_response["message_id"]
        channel_id = model_response["channel_id"]
        user_id = model_response["user_id"]

        final_response = message.strip()
        if "Assistant:" in final_response:
            parts = final_response.rsplit("Assistant:", 1)
            final_response = parts[-1].strip()

        conversation_history = read_conversation_history(user_id)
        conversation_history.append({"role": "assistant", "content": final_response})
        write_conversation_history(user_id, conversation_history)

        # if final_response.lower() not in ["skip", ""]:
        #     # Update conversation and send only the final text to Discord
        #     conversation_history.append({"role": "assistant", "content": final_response})
        #     await send_long_message(message.channel, final_response)
        #     write_conversation_history(user_id, conversation_history)
        # else:
        #     print("Assistant chose to skip the response.")

        channel = client.get_channel(channel_id)

        fetched_msg = await channel.fetch_message(message_id)
        print(f"Fetched message with ID: {fetched_msg.id}")

        await fetched_msg.edit(content=final_response)


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.lower() == "!optin":
        opted_in_users.add(str(message.author.id))
        save_opted_in_users()
        await message.channel.send(
            "You have opted in. The bot will now process all of your messages."
        )
        return

    if message.content.lower() == "!optout":
        opted_in_users.discard(str(message.author.id))
        save_opted_in_users()
        await message.channel.send(
            "You have opted out. The bot will no longer process your messages."
        )
        return

    if message.content.lower() == "!help":
        opted_in_users.discard(str(message.author.id))
        save_opted_in_users()
        await message.channel.send(
            "!optin: Allow the bot to respond to your messages.\n"
            "!optout: Make the bot ignore your messages. Active by default.\n"
            "!help: Show this help dialogue.\n"
        )
        return

    if str(message.author.id) not in opted_in_users:
        return

    if message.content:
        user_id = str(message.author.id)
        user_message = message.content
        print(f"Received message from {message.author.name}: {user_message}")

        # Read/update conversation
        conversation_history = read_conversation_history(user_id)
        conversation_history.append({"role": "user", "content": user_message})
        conversation_history = conversation_history[-20:]

        # Build prompt
        system_prompt = """
        You are Llama, a helpful assistant. You will receive snippets of dialogue labeled "User:" and "Assistant:". 
        Your task is to produce exactly one new "Assistant" response. Follow these rules:

        1. Do not fabricate or alter any user messages.
        2. Respond only as “Assistant,” using your own words (do not quote or restate user messages).
        3. Be respectful and helpful, providing a succinct answer.
        4. If the user refers to someone other than Llama, respond with "skip."
        """

        full_prompt = "System:\n" + system_prompt + "\n\nConversation:\n"
        for msg_dict in conversation_history:
            if msg_dict["role"] == "user":
                full_prompt += f"User: {msg_dict['content']}\n"
            else:
                full_prompt += f"Assistant: {msg_dict['content']}\n"

        # Let the model know we want the next assistant message
        full_prompt += "Assistant:"

        # Whenever a user sends any message, the bot will reply.
        sent_msg = await message.channel.send("Processing response!")

        # Capture and print the ID of the sent message
        msg_id = sent_msg.id
        print(f"Sent message ID: {msg_id}")

        # Send the prompt to the model
        push_query(
            json.dumps(
                {
                    "message": full_prompt,
                    "message_id": msg_id,
                    "channel_id": message.channel.id,
                    "user_id": user_id,
                }
            )
        )


client.run(DISCORD_TOKEN)
