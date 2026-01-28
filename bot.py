import discord
from discord.ext import commands
from pathlib import Path
import asyncio
from dotenv import load_dotenv
import os
import time

DEV_MODE = Path("./.ignore-guild-specific-cmds").exists()

INTENTS = discord.Intents.default()
INTENTS.message_content = True
INTENTS.members = True

# load env variables
load_dotenv(".env")
bot = commands.Bot(
    command_prefix="!",
    intents=INTENTS
)

COGS_DIR = Path("./cogs")

# startup logs guild (the Kernix Discord server)
GUILD_ID = 1440424449861226700

# send startup log
async def message_log():
    await bot.wait_until_ready()
    channel = bot.get_channel(1461371585419280526)
    ts = int(time.time())
    if channel:
        try:
            await channel.send(f"Bot started at <t:{ts}:F>")
        except Exception as e:
            print(f"❌ Failed to send start message: {e}")

bot.guild_config = {}

# get guild config
def get_guild_config(guild_id: int):
    return bot.guild_config.get(str(guild_id), {})
bot.get_guild_config = get_guild_config

async def load_cogs():
    global DEV_MODE
    if not COGS_DIR.exists():
        print("⚠️ No cogs directory found")
        return

    for folder in COGS_DIR.iterdir():
        if not folder.is_dir():
            continue

        # only load folders with markers
        if not (folder / "__init__.py").exists():
            continue

        # ignore markers
        for file in folder.glob("*.py"):
            if file.name.startswith("_"):
                continue
            ext = f"cogs.{folder.name}.{file.stem}"
            try:
                await bot.load_extension(ext)
                print(f"✅ Loaded {ext}")
            except Exception as e:
                print(f"❌ Failed to load {ext}: {e}")

# sync
async def sync_commands():
    await bot.wait_until_ready()
    # sync global commands
    try:
        await asyncio.wait_for(bot.tree.sync(), timeout=10)
        print("✅ Global commands synced")
    except asyncio.TimeoutError:
        print("⚠️ Global command sync timed out")
    except Exception as e:
        print(f"❌ Failed to sync global commands: {e}")

    # cancel guild commands sync if not Kernix
    if DEV_MODE:
        print("❌ Skipping guild command sync (Non-Kernix)")
        return

    # sync guild commands
    try:
        guild_obj = discord.Object(id=GUILD_ID)
        await asyncio.wait_for(bot.tree.sync(guild=guild_obj), timeout=10)
        print(f"✅ Commands synced for guild {GUILD_ID}")
    except asyncio.TimeoutError:
        print(f"⚠️ Guild command sync timed out for {GUILD_ID}")
    except Exception as e:
        print(f"❌ Failed to sync guild commands: {e}")

@bot.event
async def on_ready():
    ts = int(time.time())
    print(f"✅ Logged in as {bot.user} ({bot.user.id})")
    print(f"🕒 Bot started at {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(ts))}")

    # start background tasks
    asyncio.create_task(sync_commands())
    asyncio.create_task(message_log())

    # set presence
    activity = discord.Activity(type=discord.ActivityType.watching, name="github.com/LittleT6109/Kernix")
    await bot.change_presence(activity=activity)

# load cogs
async def main():
    async with bot:
        await load_cogs()
        await bot.start(os.getenv("DISCORD_TOKEN"))

# start bot
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
    	print(f"\nBot shutting down")
