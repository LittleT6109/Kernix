import discord
from discord.ext import commands
from discord import app_commands
import json, os

LEVELS_FILE = "levels.json"

class Levels(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data = self.load_levels()

    # level/xp system
    def load_levels(self):
        if os.path.exists(LEVELS_FILE):
            with open(LEVELS_FILE, "r") as f:
                return json.load(f)
        return {}

    def save_levels(self):
        with open(LEVELS_FILE, "w") as f:
            json.dump(self.data, f, indent=4)

    def get_next_level_xp(self, level: int) -> int:
        next_level = level + 1
        if next_level == 1:
            return 5
        if next_level == 2:
            return 20
        if next_level == 3:
            return 40
        if next_level == 4:
            return 75
        if next_level == 5:
            return 100
        return 100 * (next_level - 4)

    def get_sorted_users(self, gid: str):
        users = self.data.get(gid, {})
        return sorted(
            users.items(),
            key=lambda item: (-item[1]["level"], -item[1]["xp"])
        )

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return

        cfg = self.bot.get_guild_config(message.guild.id)
        if not cfg.get("leveling_enabled"):
            return
        mute_role_id = cfg.get("mute_role")
        if mute_role_id and mute_role_id in [role.id for role in message.author.roles]:
            return

        gid = str(message.guild.id)
        uid = str(message.author.id)

        if gid not in self.data:
            self.data[gid] = {}
        if uid not in self.data[gid]:
            self.data[gid][uid] = {"xp": 0, "level": 0}

        profile = self.data[gid][uid]
        profile["xp"] += 1

        needed = self.get_next_level_xp(profile["level"])
        if profile["xp"] >= needed:
            profile["level"] += 1
            profile["xp"] = 0  # reset XP on level up
            await message.channel.send(f"🎉 {message.author.mention} reached **Level {profile['level']}**!")

            for lvl, role_id in cfg.get("level_roles", {}).items():
                if profile["level"] == int(lvl):
                    role = message.guild.get_role(role_id)
                    if role:
                        await message.author.add_roles(role)

        self.save_levels()
        await self.bot.process_commands(message)

    # commands
    @app_commands.command(name="level", description="View your level and rank")
    async def level(self, interaction: discord.Interaction):
        gid = str(interaction.guild.id)
        uid = str(interaction.user.id)

        if gid not in self.data or uid not in self.data[gid]:
            await interaction.response.send_message(
                "You don’t have any XP yet",
                ephemeral=True
            )
            return

        sorted_users = self.get_sorted_users(gid)
        rank = next(i for i, (u, _) in enumerate(sorted_users, 1) if u == uid)
        profile = self.data[gid][uid]

        embed = discord.Embed(
            title="📊 Level Info",
            color=discord.Color.blurple()
        )
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        embed.add_field(name="Level", value=profile["level"], inline=True)
        embed.add_field(name="XP", value=profile["xp"], inline=True)
        embed.add_field(name="Rank", value=f"#{rank}", inline=True)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="leaderboard", description="View the server leaderboard")
    async def leaderboard(self, interaction: discord.Interaction):
        gid = str(interaction.guild.id)

        if gid not in self.data or not self.data[gid]:
            await interaction.response.send_message(
                "No leaderboard yet",
                ephemeral=True
            )
            return

        sorted_users = self.get_sorted_users(gid)

        embed = discord.Embed(
            title="🏆 Server Leaderboard",
            color=discord.Color.gold()
        )

        for i, (uid, profile) in enumerate(sorted_users[:10], start=1):
            member = interaction.guild.get_member(int(uid))
            name = member.display_name if member else f"User {uid}"

            embed.add_field(
                name=f"#{i} — {name}",
                value=f"Level **{profile['level']}** | XP `{profile['xp']}`",
                inline=False
            )

        executor_id = str(interaction.user.id)
        if executor_id in self.data[gid]:
            rank = next(
                i for i, (u, _) in enumerate(sorted_users, 1) if u == executor_id
            )
            profile = self.data[gid][executor_id]
            embed.set_footer(
                text=f"You: Level {profile['level']} • XP {profile['xp']} • Rank #{rank}"
            )

        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Levels(bot))
