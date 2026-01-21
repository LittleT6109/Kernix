import discord
from discord import app_commands
from discord.ext import commands
import random
import requests
import aiohttp
from io import BytesIO
from PIL import Image, ImageDraw

class Misc(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # get circle avatar
    async def get_circular_avatar(self, user: discord.User):
        url = user.display_avatar.url

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                avatar_bytes = await resp.read()

        avatar = Image.open(BytesIO(avatar_bytes)).convert("RGBA")

        size = avatar.size
        mask = Image.new("L", size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, size[0], size[1]), fill=255)

        circular = Image.new("RGBA", size)
        circular.paste(avatar, (0, 0), mask=mask)

        buf = BytesIO()
        circular.save(buf, format="PNG")
        buf.seek(0)
        return buf

    # /meme
    @app_commands.command(name="meme", description="Get a random meme from Reddit")
    async def meme(self, interaction: discord.Interaction):
        await interaction.response.defer()

        subreddits = ["memes", "dankmemes", "wholesomememes", "funny"]
        subreddit = random.choice(subreddits)

        url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit=100"
        headers = {"User-Agent": "DiscordBot:RandomMeme:v1.0 (by /u/littlet)"}

        try:
            res = requests.get(url, headers=headers, timeout=10).json()
            posts = res["data"]["children"]

            image_posts = [
                post for post in posts
                if post["data"].get("post_hint") == "image"
            ]

            if not image_posts:
                return await interaction.followup.send("No memes found")

            chosen = random.choice(image_posts)
            data = chosen["data"]

            embed = discord.Embed(
                title=data["title"],
                color=discord.Color.blue(),
                url=f"https://reddit.com{data['permalink']}",
            )
            embed.set_image(url=data["url"])

            await interaction.followup.send(embed=embed)

        except Exception as e:
            await interaction.followup.send(f"Failed to fetch meme\n`{e}`")

    # /whois
    @app_commands.command(name="whois", description="Show info about a user")
    @app_commands.describe(member="The member to show info for")
    async def whois(self, interaction: discord.Interaction, member: discord.Member):
        buf = await self.get_circular_avatar(member)

        embed = discord.Embed(
            title=str(member),
            color=discord.Color.blue(),
            description=(
                f"ID: `{member.id}`\n"
                f"Joined: {member.joined_at.strftime('%Y-%m-%d')}\n"
                f"Roles: {len(member.roles) - 1}"
            ),
        )

        file = discord.File(buf, filename="avatar.png")
        embed.set_thumbnail(url="attachment://avatar.png")

        await interaction.response.send_message(embed=embed, file=file)


async def setup(bot: commands.Bot):
    await bot.add_cog(Misc(bot))
