```markdown
# TiRex AI Assistant

The official AI Assistant for the TiRex Discord server, built with Python using the `discord.py` library and integrated with the Google Gemini API (`gemini-flash-lite-latest` model). The bot is designed to assist users with server information, Roblox scripting (Luau), and exploit scene news.

## Key Features

* **AI Integration**: Automatically responds to messages in a designated channel using system instructions and contextual memory.
* **Local Knowledge Base**: Dynamic context enrichment using data from `agents.md` and `live_updates.txt` files.
* **API Key Rotation**: Supports an array of Google Gemini API keys, automatically switching to the next one if an error occurs or rate limits are reached.
* **Activity Logging**: Automatically logs messages from specific tracking channels into a live updates text file to feed the knowledge base.
* **Administration Tools**: Simple channel moderation features, including channel locking and blacklisting specific users.

## Bot Commands

All administrative commands are restricted to the user specified as `ADMIN_ID` in the configuration. Default prefix: `.`

* `.clear` — Clears the AI context history for the current channel.
* `.blacklist add @user [reason]` — Bans a user from speaking in the current channel and logs the action.
* `.blacklist remove @user` — Unbans a user, restoring their channel permissions.
* `.lock` — Prevents the `@everyone` role from sending messages in the channel.
* `.unlock` — Restores standard message permissions for the channel.
* `.ping` — Checks the bot's current latency.

## Requirements

The following Python libraries are required to run this project:
* `discord.py`
* `google-generativeai`
* `psutil`

You can install the dependencies via pip:
```bash
pip install discord.py google-generativeai psutil


## Setup and Installation

1. Open `aihelper.py` and fill in the configuration variables at the top of the script:
* `DISCORD_TOKEN` — Your Discord bot token.
* `ADMIN_ID` — Your Discord user ID for accessing admin commands.
* `GEMINI_KEYS` — A list of your Google Gemini API keys.
* `AI_ASSISTANT_CHANNEL_ID` — The ID of the channel where the AI will respond.
* `LOG_CHANNELS` — Channel IDs where messages will be logged to the live updates file.
* `BLACKLIST_LOG_CHANNEL_ID` — The ID of the channel where blacklist logs will be sent.


2. Create the knowledge base files in the root directory (optional):
* `agents.md` — Core information about the server.
* `live_updates.txt` — File for recent updates (can be populated automatically via `LOG_CHANNELS`).


3. Run the bot:

```bash
python aihelper.py

```
