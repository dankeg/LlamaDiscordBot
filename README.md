# Llama Discord Bot

As the name suggests, this discord bot allows you to use the Llama LLM in your discord server. To prevent spam and unwanted messages, it allows individual users to opt in and out. It also stores conversation history and context per user, so that different conversations cannot interfere with one another. More advanced features, such as specifying the specific LLM, multi-user conversations, deleting conversation history, and more are in progress!

[Invite the bot](https://discord.com/oauth2/authorize?client_id=1292327901139828857&permissions=309237722112&integration_type=0&scope=bot)

## How it Works
At the most basic level, this project uses **PyTorch** to handle initializing, configuring, and querying the LLM. This enables many parameters, such as temperature, tokenization, padding, and hardware utilization to be tweaked and tested to optimize resource utilization, response time, and answer quality. Weights for the models used are fetched and updated from **HuggingFace**.
Thus, the basic functionality involves using the **Discord.py** library to listen for new messages, pass them to PyTorch, generate a response from the model, and present this response to the user.

To handle usage by several users simultaneously, the project utilizes a distributed architecture. When a user provides a new query, it is submitted to a **Redis** QUERY queue. Runners pop these queries and pass them to the model, pushing them to a RESPONSE queue. A scheduled updater process checks this queue, presenting responses to the user. This enables the application to grow and shrink to meet user demand, simply by adding or removing runners. Redis ensures fast messaging between components while enforcing atomicity: ensuring user queries aren't lost or duplicated. 

Each of these components are containerized using **Docker**, ensuring scalability and a standardized environment. Scaling up is as easy as increasing the number of runner containers, each of which manage themselves.

## How to Setup the Bot
If you want to run the bot locally instead, follow these instructions:

1. Install Docker
2. Clone the repo
3. Populate the `.env` file with a HuggingFace and Discord Token
4. Run `docker compose up --build` in the root of the repo

After the images finish building, the runners will perform a start-up diagnostic to ensure the selected model can be loaded and queried. Once this is done, the bot is ready to use!

## How to Use the Bot
By default, all users are ignored by the bot. To opt in, send the following message to a channel visible to the bot:

`!optin`

The bot will now read your messages if it seems relevant for it to respond. For example:

`Hey Llama, what are the train lines in Boston?`

Will return a response from the bot. The bot maintains a limited record of the conversation it had with you, to use for context in future conversations. 

If you want to opt out of using the bot, send the following to a channel visible to the bot:

`!optout`