import discord
from discord.ext import commands
from discord import app_commands
import sys, os, time
import asyncio

MOD_IDS = [1041510279634235483, 584481143802298380, 395940334078787584, 1384229409187168376, 776914808821776494]
GUILD_ID = 1440424449861226700
LOG_CHANNEL_ID = 1443296817591881930

class gearworkssmp(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def is_mod(self, user_id: int):
        return user_id in MOD_IDS

    @app_commands.command(name="restart", description="Restart the bot or a service")
    @app_commands.describe(process="What do you want to restart?")
    @app_commands.choices(process=[
        app_commands.Choice(name="Bot", value="bot"),
        app_commands.Choice(name="Minecraft Server", value="minecraft"),
        app_commands.Choice(name="Velocity Proxy", value="velocity"),
    ])
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    async def restart(self, interaction: discord.Interaction, process: app_commands.Choice[str]):
        if interaction.guild.id != GUILD_ID or not self.is_mod(interaction.user.id):
            return await interaction.response.send_message("Not permitted.", ephemeral=True)

        ts = int(time.time())

        if process.value == "bot":
            await interaction.response.send_message("🔄 Restarting bot...", ephemeral=True)
            bot.get_channel(1461373374721818746)
            if channel:
                await channel.send(f"Bot restarted at <t:{ts}:F> by <@{interaction.user.id}>")
            python = sys.executable
            os.execv(python, [python] + sys.argv)

        elif process.value == "minecraft":
            await interaction.response.defer(ephemeral=True)
            os.system("ssh -p 2062 littlet@192.168.1.38 sudo systemctl restart minecraftserver")
            await interaction.followup.send("✅ Minecraft Server restarted", ephemeral=True)
            channel = self.bot.get_channel(LOG_CHANNEL_ID)
            if channel:
                await channel.send(f"Minecraft Server restarted at <t:{ts}:F> by <@{interaction.user.id}>")

        elif process.value == "velocity":
            await interaction.response.defer(ephemeral=True)
            os.system("ssh -p 2062 littlet@192.168.1.38 sudo systemctl restart velocity")
            await interaction.followup.send("✅ Velocity restarted", ephemeral=True)
            channel = self.bot.get_channel(LOG_CHANNEL_ID)
            if channel:
                await channel.send(f"Velocity Proxy restarted at <t:{ts}:F> by <@{interaction.user.id}>")

    @app_commands.command(name="reply", description="Reply to a specific message in a channel")
    @app_commands.describe(
        channel="Channel the message is in",
        message_id="ID of the message to reply to",
        reply="Reply content"
    )
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    async def reply_cmd(self, interaction: discord.Interaction, channel: discord.TextChannel, message_id: str, reply: str):
        if interaction.guild.id != GUILD_ID or not self.is_mod(interaction.user.id):
            return await interaction.response.send_message("Not permitted.", ephemeral=True)

        try:
            msg = await channel.fetch_message(int(message_id))
            await msg.reply(reply)
            await interaction.response.send_message(f"✅ Replied to message in {channel.mention}", ephemeral=True)
        except discord.NotFound:
            await interaction.response.send_message("❌ Message not found. Check the ID.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Error:\n```py\n{e}\n```", ephemeral=True)

    @app_commands.command(name="message", description="Send a message to a specified channel")
    @app_commands.describe(channel="Channel to send the message to", message="Message to send")
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    async def message_cmd(self, interaction: discord.Interaction, channel: discord.TextChannel, message: str):
        if interaction.guild.id != GUILD_ID or not self.is_mod(interaction.user.id):
            return await interaction.response.send_message("Not permitted.", ephemeral=True)

        try:
            await channel.send(message)
            await interaction.response.send_message(f"✅ Message sent to {channel.mention}", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Failed to send message:\n```py\n{e}\n```", ephemeral=True)

    @app_commands.command(name="dm", description="DM a guild member")
    @app_commands.describe(member="The member to DM", message="The message to send")
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    async def dm(self, interaction: discord.Interaction, member: discord.Member, message: str):
        if interaction.guild.id != GUILD_ID or not self.is_mod(interaction.user.id):
            return await interaction.response.send_message("Not permitted.", ephemeral=True)

        if member.bot:
            return await interaction.response.send_message("You can't DM bots.", ephemeral=True)

        try:
            await member.send(message)
            await interaction.response.send_message(f"DM sent to {member.mention}", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message("Could not DM this user (DMs closed).", ephemeral=True)

    @app_commands.command(name="think", description="hrm...")
    @app_commands.describe(seconds='Amount of time to "hrm..."')
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    async def think(self, interaction: discord.Interaction, seconds: int):
        await interaction.response.defer()
        await asyncio.sleep(seconds)
        await interaction.followup.send(f"wow, i thinked up something good")

async def setup(bot: commands.Bot):
    await bot.add_cog(gearworkssmp(bot))
