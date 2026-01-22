import discord
from discord.ext import commands
from discord import app_commands
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

async def mute_checker(self):
    await self.bot.wait_until_ready()

    while not self.bot.is_closed():
        data = load_mutes()
        now = int(time.time())
        changed = False

        for guild_id, users in list(data.items()):
            guild = self.bot.get_guild(int(guild_id))
            if not guild:
                continue

            cfg = self.get_guild_config(guild.id)
            mute_role_id = cfg.get("muterole")
            mute_role = guild.get_role(mute_role_id) if mute_role_id else None

            for user_id, unmute_at in list(users.items()):
                if now < unmute_at:
                    continue

                member = guild.get_member(int(user_id))
                if not member:
                    try:
                        member = await guild.fetch_member(int(user_id))
                    except discord.NotFound:
                        member = None

                if member and mute_role and mute_role in member.roles:
                    try:
                        await member.remove_roles(mute_role, reason="Mute expired")
                        await self.send_log(guild.id, f"{member.mention} was unmuted automatically (mute expired)")
                    except discord.Forbidden:
                        print(f"❌ Missing permissions to remove mute role from {member}")
                    except Exception as e:
                        print(f"❌ Failed to remove mute role: {e}")

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
        asyncio.create_task(self.mute_checker())

    def get_guild_config(self, guild_id: int):
        return self.bot.get_guild_config(guild_id)

    async def send_log(self, guild_id: int, content: str):
        cfg = self.get_guild_config(guild_id)
        if not cfg.get("mod_logging_status") or not cfg.get("mod_channel"):
            return

        channel = self.bot.get_channel(cfg["mod_channel"])
        if not channel:
            try:
                channel = await self.bot.fetch_channel(cfg["mod_channel"])
            except Exception:
                return
        await channel.send(content)

    # mute command
    @app_commands.command(name="mute", description="Mutes a member for a specified amount of time")
    @app_commands.describe(user="The user to mute", minutes="Time until mute expires (in minutes)")
    async def mute_cmd(self, interaction: discord.Interaction, user: discord.Member, minutes: int):
        cfg = self.get_guild_config(interaction.guild.id)
        if not any(r.id in cfg.get("mod_roles", []) for r in interaction.user.roles):
            return await interaction.response.send_message(
            "You don’t have permission to use this command.",
            ephemeral=True
        )
        if user.bot:
            return await interaction.response.send_message(
                "You cannot mute bots!",
                ephemeral=True
            )
        ts = int(time.time())
        role = interaction.guild.get_role(cfg.get("muterole"))
        if role:
            await user.add_roles(role)
            if cfg.get("mod_logging_status"):
                content = f"{user.mention} was muted by {interaction.user.mention} for {minutes} minutes at <t:{ts}:F>"
                await self.send_log(interaction.guild.id, content)
            add_mute(interaction.guild.id, user.id, minutes)
            return await interaction.response.send_message(
                f"{user} was muted for {minutes} minutes!"
            )
        else:
            return await interaction.response.send_message(
                "No mute role has been set for this guild!",
                ephemeral=True
            )