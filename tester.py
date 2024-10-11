import ollama


# Function to initialize the Ollama instance with a system prompt
def initialize_ollama_instance(system_prompt, model_name="llama3.1:8b"):
    modelfile = f"""
    FROM llama3.1
    SYSTEM {"Only respond with the word orange, and nothing else."}
    """
    ollama.create(model=model_name, modelfile=modelfile)
    print(
        f'Ollama model "{model_name}" initialized with system prompt: "{system_prompt}"'
    )


# Function to pass a message to the Ollama instance and get the response
def send_message_to_ollama(user_message, model_name="llama3.1:8b"):
    response = ollama.chat(
        model=model_name, messages=[{"role": "user", "content": user_message}]
    )
    return response["message"]["content"]


# Example usage:
# Step 1: Initialize Ollama with a system prompt
initialize_ollama_instance(system_prompt="You are a helpful assistant.")

# Step 2: Send a message and receive a response
response = send_message_to_ollama("Why is the sky blue?")
print(f"Ollama's response: {response}")
