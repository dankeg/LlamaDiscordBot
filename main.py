import discord
import json
from pytorchimp import query_model

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

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.lower() == "!optin":
        opted_in_users.add(str(message.author.id))
        save_opted_in_users()
        await message.channel.send("You have opted in. The bot will now process all of your messages.")
        return

    if message.content.lower() == "!optout":
        opted_in_users.discard(str(message.author.id))
        save_opted_in_users()
        await message.channel.send("You have opted out. The bot will no longer process your messages.")
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
        system_prompt = (
            "You are Llama, a helpful assistant. You must not fabricate user messages.\n"
            "Only respond from the 'assistant' perspective. Always be respectful and helpful.\n"
            "When you respond, do not include additional user lines or rewrite what the user said.\n"
            "Provide your best answer succinctly.\n"
            "If a message refers to someone other than Llama, respond with 'skip'"
        )

        full_prompt = "System:\n" + system_prompt + "\n\nConversation:\n"
        for msg_dict in conversation_history:
            if msg_dict["role"] == "user":
                full_prompt += f"User: {msg_dict['content']}\n"
            else:
                full_prompt += f"Assistant: {msg_dict['content']}\n"

        # Let the model know we want the next assistant message
        full_prompt += "Assistant:"

        # Send the prompt to the model
        raw_response = query_model(full_prompt)
        print(f"Raw LLM response: {raw_response}")

        # ---------------------------------------------------
        # EXTRACT ONLY THE FINAL ASSISTANT TEXT
        # ---------------------------------------------------
        # Some models will return the entire conversation, or repeated "Assistant:" lines.
        # We'll isolate everything AFTER the last "Assistant:".
        final_response = raw_response.strip()
        if "Assistant:" in final_response:
            parts = final_response.rsplit("Assistant:", 1)
            final_response = parts[-1].strip()

        print(f"Final extracted response: {final_response}")

        if final_response.lower() not in ["skip", ""]:
            # Update conversation and send only the final text to Discord
            conversation_history.append({"role": "assistant", "content": final_response})
            await send_long_message(message.channel, final_response)
            write_conversation_history(user_id, conversation_history)
        else:
            print("Assistant chose to skip the response.")

client.run(DISCORD_TOKEN)
