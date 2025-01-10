# Llama Discord Bot

As the name suggests, this discord bot allows you to use Ollama in your discord server. To prevent spam and unwanted messages, it allows individual users to opt in and out. It also stores conversation history and context per user, so that different conversations cannot interfere with one another. More advanced features, such as specifying the specific LLM, multi-user conversations, deleting conversation history, and more are in progress!

[Invite the bot](https://discord.com/oauth2/authorize?client_id=1292327901139828857&permissions=309237722112&integration_type=0&scope=bot)

## How to Setup the Bot
1. Install Ollama
2. Clone the repo, and perform `poetry install` in the root of the repo
3. Create a file license.txt, and paste in your discord bot token
4. Run main.py!

## How to Use the Bot
By default, all users are ignored by the bot. To opt in, send the following message to a channel visible to the bot:

`!optin`

The bot will now read your messages if it seems relevant for it to respond. For example:

`Hey Llama, what are the train lines in Boston?`

Will return a response from the bot. The bot maintains a record of the conversation it had with you, to use for context in future conversations. 

If you want to opt out of using the bot, send the following to a channel visible to the bot:

`!optout`