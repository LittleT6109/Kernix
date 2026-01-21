import discord
from discord.ext import commands
import random

class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # on join
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        cfg = self.bot.get_guild_config(member.guild.id)

        # welcome message
        if cfg.get("welcome_channel") and cfg.get("welcome_messages"):
            channel = member.guild.get_channel(cfg["welcome_channel"])
            if channel:
                msg = random.choice(cfg["welcome_messages"])
                await channel.send(msg.replace("{user}", member.mention))

        # autorole
        if cfg.get("autorole"):
            role = member.guild.get_role(cfg["autorole"])
            if role:
                await member.add_roles(role)


async def setup(bot):
    await bot.add_cog(Welcome(bot))
