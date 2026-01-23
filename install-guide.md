# Installing

This guide will show you how to install and run your own bot based on this code

## Cloning the repository

Use `git clone https://github.com/LittleT6109/Kernix` in your terminal to clone the repository. This will create a folder named "Kernix" in the current working directory. You can rename this to whatever you want.

## Setup

Use `cd <FOLDER_NAME_HERE>` to enter the bot directory. You will need to create a `.env` file. Open that file with your text editor of choice. In that file, put `DISCORD_TOKEN=<BOT_TOKEN_HERE>`

### Getting a token

Go to https://discord.com/developers/applications in your browser. Create a new app, name it anything. Enter the "Bot" section in the left sidebar, scroll down and click "Reset Token", tt may ask you for verification. Copy the new token it generates, and replace <BOT_TOKEN_HERE> with that in the .env file.

### Inviting the bot

Remain in the Bot section in the left sidebar. Enable Server Members Intent, and Message Content Intent. Then scroll down and select "Administrator" in bot permissions.
Go to the OAuth2 section in the left sidebar. Choose "bot" in the scopes section. Then scroll down and select "Administrator" again. Copy the link it gives and paste it in your browser.

## Starting the bot

You will need python installed.

### venv

On some Linux distros, you will need a venv to prevent breaking system packages. You can generate one by running `python -m venv venv` in the bot folder. Before installing the below dependencies, run this in the bot directory: `source venv/bin/activate`. You should see a `(venv)` appear to the left of your prompt.

### Pip dependencies:

- discord.py
- pillow
- python-dotenv
- requests

You can install these with `pip install <package-name>`

### Removing Kernix-only cogs

You can remove the guild-specific folder from the cogs folder entirely, these are for Kernix only.

### Running the bot

if you do not need a venv:
You can either double click the bot.py file, or navigate to the bot directory in your terminal and run it with `python3 bot.py` (`python bot.py` on windows)

If you need a venv:
You cannot double click the bot.py file to run. You must navigate to the bot directory in your terminal, and run `source venv/bin/activate`. You should see a `(venv)` appear to the left of your prompt, you can now safely run the bot with `python3 bot.py`.