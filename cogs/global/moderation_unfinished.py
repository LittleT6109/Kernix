import discord
from discord.ext import commands
import time
import json
from pathlib import Path
import asyncio

MUTE_FILE = Path("mutes.json")

def load_mutes():
    if not MUTE_FILE.exists():
        return {}
    with open(MUTE_FILE, "r") as f:
        return json.load(f)

def save_mutes(data):
    with open(MUTE_FILE, "w") as f:
        json.dump(data, f, indent=2)

def add_mute(guild_id, user_id, minutes):
    data = load_mutes()
    unmute_at = int(time.time() + minutes * 60)

    guild_id = str(guild_id)
    user_id = str(user_id)

    data.setdefault(guild_id, {})[user_id] = unmute_at
    save_mutes(data)

async def mute_checker(bot):
    await bot.wait_until_ready()

    while not bot.is_closed():
        data = load_mutes()
        now = int(time.time())
        changed = False

        for guild_id, users in list(data.items()):
            for user_id, unmute_at in list(users.items()):
                if now >= unmute_at:
                    # unmute role here
                    del data[guild_id][user_id]
                    changed = True

            if not data[guild_id]:
                del data[guild_id]

        if changed:
            save_mutes(data)

        await asyncio.sleep(60)

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_guild_config(self, guild_id: int):
        return self.bpt.get_guild_config(guild_id)

    async def send_log(self, guild_id: int, content: str):
        cfg = self.get_guild_config(guild_id)
        if not cfg.get("mod_logging_status") or not cfg.get("mod_log_channel"):
            return

        channel = self.bot.get_channel(cfg["mod_log_channel"])
        if not channel:
            try:
                channel = await
                self.bot.fetch_channel(cfg["mod_log_channel"])
            except Exception
                return
        await channel.send(content)

    @app_commands.command(name="mute", description="Mutes a member for a specified amount of time")
    @app_commands.describe(user="The user to mute", time="Time until mute expires (in minutes)")
    async def mute_cmd(self, interaction: discord.Interaction, user: discord.Member, time: int):
        ts = int(time.time())
        role = cfg.get("muterole")
        if role:
            await member.add_roles(role)
            if cfg.get("mod_logging"):
                content = f"{user.mention} was muted by {interaction.user.mention} for {time} minutes"
                send_log(content)
            add_mute(interaction.guild.id, user.id, time)
