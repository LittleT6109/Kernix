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
### Pip dependencies:
- discord.py
- pillow
- python-dotenv
You can install these with `pip install <package-name>`

### Running the bot
You can either double click the bot.py file, or navigate to the bot directory in your terminal and run it with `python3 bot.py` (`python bot.py` on windows)
