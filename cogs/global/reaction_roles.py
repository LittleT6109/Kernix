import discord
from discord.ext import commands
from discord import app_commands
import json
from pathlib import Path

RR_FILE = Path("reaction_roles.json")

class ReactionRoles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def _load(self):
        if not RR_FILE.exists():
            return {}
        with open(RR_FILE, "r") as f:
            return json.load(f)

    def _save(self, data):
        with open(RR_FILE, "w") as f:
            json.dump(data, f, indent=2)

    def get_guild_config(self, guild_id: int):
        return self.bot.get_guild_config(guild_id)

    # command
    @app_commands.command(name="reactionrole", description="Create a reaction role message")
    @app_commands.describe(
        channel="Channel to send the message in",
        emoji1="First emoji",
        role1="First role",
        emoji2="Second emoji (optional)",
        role2="Second role (optional)",
        emoji3="Third emoji (optional)",
        role3="Third role (optional)",
        emoji4="Fourth emoji (optional)",
        role4="Fourth role (optional)",
        emoji5="Fifth emoji (optional)",
        role5="Fifth role (optional)",
        emoji6="Sixth emoji (optional)",
        role6="Sixth role (optional)",
        emoji7="Seventh emoji (optional)",
        role7="Seventh role (optional)",
        emoji8="Eighth emoji (optional)",
        role8="Eighth role (optional)",
        emoji9="Ninth emoji (optional)",
        role9="Ninth role (optional)",
        emoji10="Tenth emoji (optional)",
        role10="Tenth role (optional)"
    )
    async def reactionrole(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel,
        emoji1: str,
        role1: discord.Role,
        emoji2: str = None,
        role2: discord.Role = None,
        emoji3: str = None,
        role3: discord.Role = None,
        emoji4: str = None,
        role4: discord.Role = None,
        emoji5: str = None,
        role5: discord.Role = None,
        emoji6: str = None,
        role6: discord.Role = None,
        emoji7: str = None,
        role7: discord.Role = None,
        emoji8: str = None,
        role8: discord.Role = None,
        emoji9: str = None,
        role9: discord.Role = None,
        emoji10: str = None,
        role10: discord.Role = None
    ):
        cfg = self.get_guild_config(interaction.guild.id)
        if not any(r.id in cfg.get("mod_roles", []) for r in interaction.user.roles):
            return await interaction.response.send_message(
                "You don’t have permission to use this command.", ephemeral=True
            )

        await interaction.response.defer(ephemeral=True)

        pairs = [
            (emoji1, role1), (emoji2, role2), (emoji3, role3), (emoji4, role4),
            (emoji5, role5), (emoji6, role6), (emoji7, role7), (emoji8, role8),
            (emoji9, role9), (emoji10, role10)
        ]
        pairs = [(e, r) for e, r in pairs if e and r]

        if not pairs:
            return await interaction.followup.send("You must provide at least one emoji and role pair.")

        lines = [f"{e} → {r.mention}" for e, r in pairs]
        content = "**React to get a role:**\n\n" + "\n".join(lines)

        msg = await channel.send(content, allowed_mentions=discord.AllowedMentions.none())

        for emoji, _ in pairs:
            try:
                await msg.add_reaction(emoji)
            except Exception as e:
                print(f"Failed to add reaction {emoji}: {e}")

        data = self._load()
        guild_id = str(interaction.guild.id)
        msg_id = str(msg.id)
        data.setdefault(guild_id, {})
        data[guild_id][msg_id] = {str(e): r.id for e, r in pairs}
        self._save(data)

        pairs_str = "\n".join([f"{e} → {r.mention}" for e, r in pairs])
        await interaction.followup.send(
            f"Reaction role message created in {channel.mention}:\n{pairs_str}"
        )

    # listeners
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        if payload.user_id == self.bot.user.id:
            return

        data = self._load()
        guild_id = str(payload.guild_id)
        msg_id = str(payload.message_id)
        emoji = str(payload.emoji)

        role_id = data.get(guild_id, {}).get(msg_id, {}).get(emoji)
        if not role_id:
            return

        guild = self.bot.get_guild(payload.guild_id)
        member = guild.get_member(payload.user_id)
        role = guild.get_role(role_id)
        if member and role:
            await member.add_roles(role)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        data = self._load()
        guild_id = str(payload.guild_id)
        msg_id = str(payload.message_id)
        emoji = str(payload.emoji)

        role_id = data.get(guild_id, {}).get(msg_id, {}).get(emoji)
        if not role_id:
            return

        guild = self.bot.get_guild(payload.guild_id)
        member = guild.get_member(payload.user_id)
        role = guild.get_role(role_id)
        if member and role:
            await member.remove_roles(role)

    @commands.Cog.listener()
    async def on_raw_message_delete(self, payload: discord.RawMessageDeleteEvent):
        data = self._load()
        guild_id = str(payload.guild_id)
        msg_id = str(payload.message_id)

        if guild_id in data and msg_id in data[guild_id]:
            del data[guild_id][msg_id]
            if not data[guild_id]:
                del data[guild_id]
            self._save(data)

async def setup(bot):
    await bot.add_cog(ReactionRoles(bot))