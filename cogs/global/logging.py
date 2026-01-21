import discord
from discord.ext import commands
import time
import aiohttp
from PIL import Image, ImageDraw
from io import BytesIO

class Logs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_guild_config(self, guild_id: int):
        return self.bot.get_guild_config(guild_id)

    # get rounded avatar for embed
    async def get_circular_avatar(self, user: discord.User, radius: int = 20):
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

    # embed setup
    async def send_log(self, guild_id: int, title: str, description: str, user: discord.User = None, color=discord.Color.blurple()):
        cfg = self.get_guild_config(guild_id)
        if not cfg.get("logging_status") or not cfg.get("log_channel"):
            return

        channel = self.bot.get_channel(cfg["log_channel"])
        if not channel:
            try:
                channel = await self.bot.fetch_channel(cfg["log_channel"])
            except Exception:
                return

        embed = discord.Embed(title=title, description=description, color=color, timestamp=discord.utils.utcnow())

        if user:
            embed.set_footer(text=f"User ID: {user.id}")

        file = None
        if user:
            avatar_buf = await self.get_circular_avatar(user)
            file = discord.File(avatar_buf, filename="avatar.png")
            embed.set_thumbnail(url="attachment://avatar.png")

        await channel.send(embed=embed, file=file)

    # event listeners
    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        if message.author.bot:
            return

        desc = f"{message.author.mention} deleted a message in {message.channel.mention}.\n"
        desc += f"**Username:** {message.author.name}\n"
        desc += f"**Nickname:** {message.author.nick or 'None'}\n"

        if message.content:
            desc += f"**Content:** {message.content}"
        if message.attachments:
            att_list = "\n".join(a.url for a in message.attachments)
            desc += f"\n**Attachments:**\n{att_list}"

        await self.send_log(message.guild.id, "Message Deleted", desc, user=message.author, color=discord.Color.red())

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        if before.author.bot:
            return

        if before.content == after.content and before.attachments == after.attachments:
            return

        desc = f"{before.author.mention} edited a message in {before.channel.mention}.\n"
        desc += f"**Username:** {before.author.name}\n"
        desc += f"**Nickname:** {before.author.nick or 'None'}\n"

        if before.content or after.content:
            desc += f"**Before:** {before.content}\n**After:** {after.content}"
        if before.attachments or after.attachments:
            before_att = "\n".join(a.url for a in before.attachments)
            after_att = "\n".join(a.url for a in after.attachments)
            desc += f"\n**Attachments Before:**\n{before_att}\n**Attachments After:**\n{after_att}"

        await self.send_log(before.guild.id, "Message Edited", desc, user=before.author, color=discord.Color.orange())

    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        logs = []

        if before.name != after.name:
            logs.append((f"{after.mention} changed their username.", f"**Before:** {before.name}\n**After:** {after.name}", after))
        if before.nick != after.nick:
            old_nick = before.nick or before.name
            new_nick = after.nick or after.name
            logs.append((f"{after.mention} changed their nickname.", f"**Before:** {old_nick}\n**After:** {new_nick}", after))

        for title, desc, user in logs:
            desc = f"{user.mention}\n**Username:** {user.name}\n**Nickname:** {user.nick or 'None'}\n{desc}"
            await self.send_log(before.guild.id, title, desc, user=user, color=discord.Color.gold())

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        desc = f"{member.mention} joined the server.\n**Username:** {member.name}\n**Nickname:** {member.nick or 'None'}"
        await self.send_log(member.guild.id, "Member Joined", desc, user=member, color=discord.Color.green())

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        desc = f"{member.mention} left the server.\n**Username:** {member.name}\n**Nickname:** {member.nick or 'None'}"
        await self.send_log(member.guild.id, "Member Left", desc, user=member, color=discord.Color.dark_red())

    @commands.Cog.listener()
    async def on_invite_create(self, invite: discord.Invite):
        user = invite.inviter
        nickname = getattr(user, "nick", None) or getattr(user, "display_name", user.name)
    
        desc = f"{user.mention} created an invite to {invite.guild.name}.\n"
        desc += f"**Username:** {user.name}\n**Nickname:** {nickname}\n"
        desc += f"**Invite Code:** {invite.code}\n**Max Uses:** {invite.max_uses or 'Unlimited'}"

        await self.send_log(invite.guild.id, "Invite Created", desc, user=user, color=discord.Color.blue())

async def setup(bot: commands.Bot):
    await bot.add_cog(Logs(bot))