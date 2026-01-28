import discord
from discord.ext import commands
from discord import app_commands
import time
import json
from pathlib import Path
import asyncio
from io import BytesIO
from PIL import Image, ImageDraw
import aiohttp

MUTE_FILE = Path("mutes.json")

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_load(self):
        self.mute_task = asyncio.create_task(self._mute_checker())

    def _load_mutes(self):
        if not MUTE_FILE.exists():
            return {}
        with open(MUTE_FILE, "r") as f:
            return json.load(f)

    def _save_mutes(self, data):
        with open(MUTE_FILE, "w") as f:
            json.dump(data, f, indent=2)

    def _add_mute(self, guild_id, user_id, minutes):
        data = self._load_mutes()
        guild_id = str(guild_id)
        user_id = str(user_id)

        unmute_at = int(time.time() + minutes * 60)

        guild_data = data.setdefault(guild_id, {})
        user_data = guild_data.get(user_id, {})

        times_muted = user_data.get("times_muted", 0) + 1

        guild_data[user_id] = {
            "unmute_at": unmute_at,
            "times_muted": times_muted
        }

        self._save_mutes(data)
        print(f"Saving mute: {guild_id=} {user_id=} times_muted={times_muted}")

    async def _mute_checker(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            data = self._load_mutes()
            now = int(time.time())
            changed = False

            for guild_id, users in list(data.items()):
                guild = self.bot.get_guild(int(guild_id))
                if not guild:
                    continue

                cfg = self.get_guild_config(guild.id)
                mute_role_id = cfg.get("mute_role")
                mute_role = guild.get_role(mute_role_id) if mute_role_id else None

                for user_id, info in list(users.items()):
                    unmute_at = info.get("unmute_at")
                    if unmute_at is None:
                        continue
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
                            await self.send_log(
                                guild.id,
                                title="Member Unmuted",
                                description=f"{member.mention} was unmuted automatically (mute expired)",
                                user=member,
                                color=discord.Color.green()
                            )
                        except discord.Forbidden:
                            print(f"❌ Missing permissions to remove mute role from {member}")
                        except Exception as e:
                            print(f"❌ Failed to remove mute role: {e}")

                    data[guild_id][user_id]["unmute_at"] = None
                    changed = True


            if changed:
                self._save_mutes(data)

            await asyncio.sleep(60)

    async def _get_circular_avatar(self, user: discord.User, radius: int = 20):
        url = user.display_avatar.url
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                avatar_bytes = await resp.read()

        avatar = Image.open(BytesIO(avatar_bytes)).convert("RGBA")
        width, height = avatar.size

        mask = Image.new("L", (width, height), 0)
        draw = ImageDraw.Draw(mask)
        draw.rounded_rectangle((0, 0, width, height), radius=radius, fill=255)

        rounded = Image.new("RGBA", (width, height))
        rounded.paste(avatar, (0, 0), mask=mask)

        buf = BytesIO()
        rounded.save(buf, format="PNG")
        buf.seek(0)
        return buf

    async def send_log(self, guild_id: int, title: str, description: str, user: discord.User = None, color=discord.Color.blurple()):
        cfg = self.get_guild_config(guild_id)
        if not cfg.get("mod_logging_status") or not cfg.get("mod_channel"):
            return

        channel = self.bot.get_channel(cfg["mod_channel"])
        if not channel:
            try:
                channel = await self.bot.fetch_channel(cfg["mod_channel"])
            except Exception:
                return

        embed = discord.Embed(
            title=title,
            description=description,
            color=color,
            timestamp=discord.utils.utcnow()
        )

        if user:
            embed.set_footer(text=f"User ID: {user.id}")
            avatar_buf = await self._get_circular_avatar(user)
            file = discord.File(avatar_buf, filename="avatar.png")
            embed.set_thumbnail(url="attachment://avatar.png")
        else:
            file = None

        await channel.send(embed=embed, file=file)

    def get_guild_config(self, guild_id: int):
        return self.bot.get_guild_config(guild_id)

    # mute
    @app_commands.command(name="mute", description="Mutes a member for a specified amount of time")
    @app_commands.describe(user="The user to mute", minutes="Time until mute expires (in minutes)")
    async def mute_cmd(self, interaction: discord.Interaction, user: discord.Member, minutes: int):
        await interaction.response.defer(ephemeral=True)
        cfg = self.get_guild_config(interaction.guild.id)
        member = interaction.guild.get_member(interaction.user.id)
        if not member:
            member = await interaction.guild.fetch_member(interaction.user.id)
        if not any(r.id in cfg.get("mod_roles", []) for r in member.roles):
            return await interaction.followup.send(
                "You don’t have permission to use this command.",
                ephemeral=True
            )
        if user.bot:
            return await interaction.followup.send(
                "You cannot mute bots!",
                ephemeral=True
            )

        role = interaction.guild.get_role(cfg.get("mute_role"))
        if not role:
            return await interaction.followup.send(
                "No mute role has been set for this guild!",
                ephemeral=True
            )

        if role in user.roles:
            return await interaction.followup.send(
                f"{user} is already muted.",
                ephemeral=True
            )

        await user.add_roles(role)
        if cfg.get("mod_logging_status"):
            data = self._load_mutes()
            guild_data = data.get(str(interaction.guild.id), {})
            user_data = guild_data.get(str(user.id), {})

            count = user_data.get("times_muted", 0) + 1
            description = f"{user.mention} was muted by {interaction.user.mention} for {minutes}\nTimes muted: {count}"
            await self.send_log(
                interaction.guild.id,
                title="Member Muted",
                description=description,
                user=user,
                color=discord.Color.orange()
            )

        self._add_mute(interaction.guild.id, user.id, minutes)
        await interaction.followup.send(f"{user} was muted for {minutes} minutes!")

    # unmute
    @app_commands.command(name="unmute", description="Unmutes a member manually")
    @app_commands.describe(user="The user to unmute")
    async def unmute_cmd(self, interaction: discord.Interaction, user: discord.Member):
        await interaction.response.defer(ephemeral=True)
        cfg = self.get_guild_config(interaction.guild.id)
        if not any(r.id in cfg.get("mod_roles", []) for r in interaction.user.roles):
            return await interaction.followup.send(
                "You don’t have permission to use this command.",
                ephemeral=True
            )

        role = interaction.guild.get_role(cfg.get("mute_role"))
        if not role:
            return await interaction.followup.send(
                "No mute role has been set for this guild!",
                ephemeral=True
            )

        if role not in user.roles:
            return await interaction.followup.send(
                f"{user} isn’t muted.",
                ephemeral=True
            )

        try:
            await user.remove_roles(role, reason=f"Unmuted by {interaction.user}")
            await self.send_log(
                interaction.guild.id,
                title="Member Unmuted",
                description=f"{user.mention} was unmuted by {interaction.user.mention}",
                user=user,
                color=discord.Color.green()
            )

            data = self._load_mutes()
            guild_id = str(interaction.guild.id)
            user_id = str(user.id)
            if guild_id in data and user_id in data[guild_id]:
                data[guild_id][user_id]["unmute_at"] = None
                self._save_mutes(data)

            await interaction.followup.send(f"{user} was unmuted successfully!")
        except discord.Forbidden:
            await interaction.followup.send(
                "I don’t have permission to remove that role!",
                ephemeral=True
            )

    # ban
    @app_commands.command(name="ban", description="Bans a member from the server")
    @app_commands.describe(user="The user to ban", reason="Reason for the ban")
    async def ban_cmd(self, interaction: discord.Interaction, user: discord.Member, reason: str = "No reason provided"):
        cfg = self.get_guild_config(interaction.guild.id)
        if not any(r.id in cfg.get("mod_roles", []) for r in interaction.user.roles):
            return await interaction.response.send_message(
                "You don’t have permission to use this command.",
                ephemeral=True
            )
        if user == interaction.user:
            return await interaction.response.send_message(
                "You can't ban yourself!",
                ephemeral=True
            )
        if user.bot:
            return await interaction.response.send_message(
                "You cannot ban bots!",
                ephemeral=True
            )
        try:
            await interaction.guild.ban(user, reason=f"{reason} (by {interaction.user})")
            await self.send_log(
                interaction.guild.id,
                title="Member Banned",
                description=f"{user.mention} was banned by {interaction.user.mention}\nReason: {reason}",
                user=user,
                color=discord.Color.red()
            )
            await interaction.response.send_message(f"{user} was banned! 🚫")
        except discord.Forbidden:
            await interaction.response.send_message(
                "I don’t have permission to ban that member!",
                ephemeral=True
            )

    # unban
    @app_commands.command(name="unban", description="Unbans a member from the server")
    @app_commands.describe(user_id="The ID of the user to unban")
    async def unban_cmd(self, interaction: discord.Interaction, user_id: str):
        cfg = self.get_guild_config(interaction.guild.id)
        if not any(r.id in cfg.get("mod_roles", []) for r in interaction.user.roles):
            return await interaction.response.send_message("You don’t have permission to use this command.", ephemeral=True)

        try:
            user_id = int(user_id)
            user = None

            async for entry in interaction.guild.bans():
                if entry.user.id == user_id: user = entry.user; break

            if not user:
                return await interaction.response.send_message(f"No banned user with ID {user_id} found.", ephemeral=True)

            await interaction.guild.unban(user, reason=f"Unbanned by {interaction.user}")
            await self.send_log(interaction.guild.id, title="Member Unbanned",
                description=f"{user.mention} was unbanned by {interaction.user.mention}",
                user=user, color=discord.Color.green()
            )
            await interaction.response.send_message(f"{user} was unbanned successfully! ✅")

        except ValueError:
            await interaction.response.send_message("That’s not a valid user ID.", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message("I don’t have permission to unban members!", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"Failed to unban: {e}", ephemeral=True)


    # kick
    @app_commands.command(name="kick", description="Kicks a member from the server")
    @app_commands.describe(user="The user to kick", reason="Reason for the kick")
    async def kick_cmd(self, interaction: discord.Interaction, user: discord.Member, reason: str = "No reason provided"):
        cfg = self.get_guild_config(interaction.guild.id)
        if not any(r.id in cfg.get("mod_roles", []) for r in interaction.user.roles):
            return await interaction.response.send_message(
                "You don’t have permission to use this command.",
                ephemeral=True
            )
        if user == interaction.user:
            return await interaction.response.send_message(
                "You can't kick yourself!",
                ephemeral=True
            )
        if user.bot:
            return await interaction.response.send_message(
                "You cannot kick bots!",
                ephemeral=True
            )
        try:
            await interaction.guild.kick(user, reason=f"{reason} (by {interaction.user})")
            await self.send_log(
                interaction.guild.id,
                title="Member Kicked",
                description=f"{user.mention} was kicked by {interaction.user.mention}\nReason: {reason}",
                user=user,
                color=discord.Color.orange()
            )
            await interaction.response.send_message(f"{user} was kicked!")
        except discord.Forbidden:
            await interaction.response.send_message(
                "I don’t have permission to kick that member!",
                ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message(f"Failed to kick: {e}", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(Moderation(bot))