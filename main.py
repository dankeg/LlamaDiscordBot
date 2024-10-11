import discord
import json

# Set up intents to listen for messages
intents = discord.Intents.default()
intents.message_content = True  # Enable intent to read message content

client = discord.Client(intents=intents)

# Discord bot token

token_file = open("license.txt", "r")
token_key = token_file.read()

DISCORD_TOKEN = token_key

import ollama

# Initialize an empty set to store opted-in users
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
    # Split the message into chunks of `chunk_size`
    for i in range(0, len(message), chunk_size):
        # Slice the message into chunks of size `chunk_size`
        chunk = message[i : i + chunk_size]
        await channel.send(chunk)


# Function to initialize the Ollama instance with a system prompt
def initialize_ollama_instance(system_prompt, model_name="llama3.1:8b"):
    modelfile = f"""
    FROM {model_name}
    SYSTEM {system_prompt}
    """
    ollama.create(model=model_name, modelfile=modelfile)
    print(f'Ollama model "{model_name}" initialized with system prompt.')


# Function to pass messages to the Ollama instance and get the response
def send_message_to_ollama(conversation_history, model_name="llama3.1:8b"):
    response = ollama.chat(model=model_name, messages=conversation_history)
    return response["message"]["content"]


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


system_prompt_new = (
    "You are Llama, a helpful assistant. Engage in conversations naturally, "
    "providing informative and friendly responses. Always be respectful and helpful. "
    "Respond to messages directly addressed to you or containing your name 'Llama'. "
    "If the message is not directed at you, you may ignore it."
)

# Initialize Ollama with the new system prompt
initialize_ollama_instance(system_prompt=system_prompt_new)


@client.event
async def on_ready():
    print(f"Logged in as {client.user}")
    load_opted_in_users()
    print(f"Loaded opted-in users: {opted_in_users}")


@client.event
async def on_message(message):
    # Don't let the bot reply to itself
    if message.author == client.user:
        return

    # Process opt-in and opt-out commands
    if message.content.lower() == "!optin":
        opted_in_users.add(str(message.author.id))
        save_opted_in_users()
        await message.channel.send(
            "You have opted in. The bot will now process your messages."
        )
        return

    if message.content.lower() == "!optout":
        opted_in_users.discard(str(message.author.id))
        save_opted_in_users()
        await message.channel.send(
            "You have opted out. The bot will no longer process your messages."
        )
        return

    # Check if user is opted in
    if str(message.author.id) not in opted_in_users:
        return  # Ignore messages from users who have not opted in

    # Proceed to process the message
    if message.content:
        user_id = str(message.author.id)
        user_message = message.content
        print(f"Received message from {message.author.name}: {user_message}")

        # Read conversation history
        conversation_history = read_conversation_history(user_id)

        # Append the user's message to the conversation history
        conversation_history.append({"role": "user", "content": user_message})

        # Limit conversation history to last 10 messages to manage context length
        conversation_history = conversation_history[-20:]

        # Send conversation history to Ollama
        response = send_message_to_ollama(conversation_history)
        api_response = response.strip()
        print(f"LLM response: {api_response}")

        # Check if the response is appropriate
        if api_response.lower() not in ["skip", ""]:
            # Append the assistant's response to the conversation history
            conversation_history.append({"role": "assistant", "content": api_response})
            # Send the response back to the Discord channel
            await send_long_message(message.channel, api_response)
            # Update conversation history
            write_conversation_history(user_id, conversation_history)
        else:
            print("Assistant chose to skip the response.")


# Run the bot
client.run(DISCORD_TOKEN)
