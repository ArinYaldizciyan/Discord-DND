# Discord D&D Dungeon Master

A Discord bot that uses AI to run D&D campaigns. This bot serves as an automated Dungeon Master, allowing players to create characters, join campaigns, and embark on adventures.

## Features

- **Campaign Creation**: Set up new D&D campaigns with custom themes
- **Character Creation**: Create characters with names and classes
- **AI Dungeon Master**: Powered by LLM integration to run campaigns
- **Discord Integration**: Play D&D directly in your Discord server

## Prerequisites

- Python 3.8+
- [Ollama](https://ollama.ai/) installed locally (for the AI agent)
- A Discord Bot Token (see [Discord Developer Portal](https://discord.com/developers/applications))

## Installation

1. Clone this repository:

2. Set up a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use: venv\Scripts\activate
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

4. Create a `.env` file with your Discord bot token:
   ```
   DISCORD_BOT_KEY=your_discord_bot_token_here
   ```

5. Make sure Ollama is running with the llama3.2 model:
   ```
   ollama run llama3.2
   ```

## Usage

### Running the Bot

To start the Discord bot:

```
python bot.py
```

### Commands

- `/setup_campaign` - Create a new D&D campaign
- `/start_campaign` - Begin a campaign you've created

### Playing a Campaign

1. Use `/setup_campaign` to create a new campaign
2. Players can join by clicking the "Join Campaign" button
3. Each player creates their character through a modal form
4. The campaign owner uses `/start_campaign` to begin the adventure
5. The AI Dungeon Master takes over to guide the story

## Project Structure

- `bot.py` - Discord bot implementation with campaign management
- `agent.py` - AI agent implementation using LangChain
- `tools.py` - Tools for the AI agent including dice rolling
- `discord/` - Discord-specific utilities
  - `action_row.py` - UI components for Discord
  - `modals.py` - Modal forms for character/campaign creation

## License

MIT

## Acknowledgments

- Built with [discord-py-interactions](https://github.com/interactions-py/library)
- AI capabilities powered by [LangChain](https://langchain.com/) and [Ollama](https://ollama.ai/) 