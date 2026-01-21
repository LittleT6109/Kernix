import discord
from discord.ext import commands
from discord import app_commands
import json, os

CONFIG_FILE = "guild_config.json"

class Config(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.guild_config = self.load_config()

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        return {}

    def save_config(self):
        with open(CONFIG_FILE, "w") as f:
            json.dump(self.bot.guild_config, f, indent=4)

    @app_commands.command(name="config", description="Open server config menu")
    async def config(self, interaction: discord.Interaction):
        if interaction.user.id != interaction.guild.owner_id and not any(
            r.permissions.administrator for r in interaction.user.roles
        ):
            return await interaction.response.send_message("You must be server owner/admin!", ephemeral=True)

        await interaction.response.send_message(
            "Select an option to configure:",
            view=ConfigMenu(self, interaction.guild),
            ephemeral=True
        )

# config menu
class ConfigMenu(discord.ui.View):
    def __init__(self, cog, guild):
        super().__init__(timeout=None)
        self.cog = cog
        self.guild = guild
        self.add_item(ConfigOptionSelect(cog, guild))
        self.add_item(DoneButton())

class ConfigOptionSelect(discord.ui.Select):
    def __init__(self, cog, guild):
        options = [
            discord.SelectOption(label="Set Welcome Channel", description="Pick a channel for welcomes"),
            discord.SelectOption(label="Set Welcome Messages", description="Edit the welcome messages"),
            discord.SelectOption(label="Set Autorole", description="Pick a role for new members"),
            discord.SelectOption(label="Toggle Logging", description="Enable/Disable logging"),
            discord.SelectOption(label="Set Log Channel", description="Pick the channel for logs"),
            discord.SelectOption(label="Set Mod Roles", description="Pick roles for moderators"),
            discord.SelectOption(label="Toggle Leveling", description="Enable/Disable leveling"),
            discord.SelectOption(label="Set Level Roles", description="Assign roles unlocked at levels")
        ]
        super().__init__(placeholder="Choose an option...", options=options, min_values=1, max_values=1)
        self.cog = cog
        self.guild = guild

    async def callback(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        if guild_id not in self.cog.bot.guild_config:
            self.cog.bot.guild_config[guild_id] = {
                "welcome_channel": None,
                "welcome_messages": [],
                "autorole": None,
                "logging_status": False,
                "log_channel": None,
                "mod_roles": [],
                "leveling_enabled": False,
                "level_roles": {}
            }

        choice = self.values[0]

        if choice == "Set Welcome Channel":
            await interaction.response.send_message(
                "Select the welcome channel:",
                view=ChannelSelectView(self.cog, guild_id, key="welcome_channel"),
                ephemeral=True
            )
        elif choice == "Set Welcome Messages":
            await interaction.response.send_modal(WelcomeMessagesModal(self.cog, guild_id))
        elif choice == "Set Autorole":
            await interaction.response.send_message(
                "Select the autorole:",
                view=RoleSelectView(self.cog, guild_id, "autorole"),
                ephemeral=True
            )
        elif choice == "Toggle Logging":
            await interaction.response.send_message(
                "Toggle logging:",
                view=ToggleView(self.cog, guild_id, "logging_status"),
                ephemeral=True
            )
        elif choice == "Set Log Channel":
            await interaction.response.send_message(
                "Select the log channel:",
                view=ChannelSelectView(self.cog, guild_id, key="log_channel"),
                ephemeral=True
            )
        elif choice == "Set Mod Roles":
            await interaction.response.send_message(
                "Select mod roles:",
                view=RoleSelectView(self.cog, guild_id, "mod_roles", multiple=True),
                ephemeral=True
            )
        elif choice == "Toggle Leveling":
            await interaction.response.send_message(
                "Toggle leveling system:",
                view=ToggleView(self.cog, guild_id, "leveling_enabled"),
                ephemeral=True
            )
        elif choice == "Set Level Roles":
            await interaction.response.send_message(
                "Pick a role for a level:",
                view=LevelRoleSetupView(self.cog, guild_id),
                ephemeral=True
            )

# done button
class DoneButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Done", style=discord.ButtonStyle.green)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message("✅ Configuration complete!", ephemeral=True)
        self.view.stop()

# channel selection
class ChannelSelectView(discord.ui.View):
    def __init__(self, cog, guild_id, key="welcome_channel"):
        super().__init__(timeout=None)
        self.cog = cog
        self.guild_id = guild_id
        self.key = key
        self.add_item(ChannelSelect(cog, guild_id, key))

class ChannelSelect(discord.ui.Select):
    def __init__(self, cog, guild_id, key):
        options = [discord.SelectOption(label=c.name, value=str(c.id)) for c in cog.bot.get_guild(int(guild_id)).channels if isinstance(c, discord.TextChannel)]
        super().__init__(placeholder="Pick a channel...", options=options)
        self.cog = cog
        self.guild_id = guild_id
        self.key = key

    async def callback(self, interaction: discord.Interaction):
        channel_id = int(self.values[0])
        self.cog.bot.guild_config[self.guild_id][self.key] = channel_id
        self.cog.save_config()
        await interaction.response.send_message(f"✅ {self.key.replace('_',' ').title()} set.", ephemeral=True)
        self.view.stop()

# welcome message
class WelcomeMessagesModal(discord.ui.Modal, title="Welcome Messages"):
    messages = discord.ui.TextInput(
        label="Enter welcome messages separated by new lines",
        style=discord.TextStyle.paragraph,
        placeholder="Use {user} to mention new members. Type 'skip' to leave empty."
    )

    def __init__(self, cog, guild_id):
        super().__init__()
        self.cog = cog
        self.guild_id = guild_id

    async def on_submit(self, interaction: discord.Interaction):
        # if user typed skip, set to empty list
        if self.messages.value.strip().lower() == "skip":
            self.cog.bot.guild_config[self.guild_id]["welcome_messages"] = []
            saved_count = 0
        else:
            self.cog.bot.guild_config[self.guild_id]["welcome_messages"] = self.messages.value.splitlines()
            saved_count = len(self.messages.value.splitlines())

        self.cog.save_config()
        await interaction.response.send_message(
            f"✅ Welcome messages saved ({saved_count} messages).", ephemeral=True)

# role selection
class RoleSelectView(discord.ui.View):
    def __init__(self, cog, guild_id, key, multiple=False):
        super().__init__(timeout=None)
        self.cog = cog
        self.guild_id = guild_id
        self.key = key
        self.multiple = multiple
        self.add_item(RoleSelect(cog, guild_id, key, multiple))

class RoleSelect(discord.ui.Select):
    def __init__(self, cog, guild_id, key, multiple=False):
        options = [discord.SelectOption(label=r.name, value=str(r.id)) for r in cog.bot.get_guild(int(guild_id)).roles if not r.is_default()]
        super().__init__(placeholder="Pick role(s)...", options=options, min_values=1, max_values=len(options) if multiple else 1)
        self.cog = cog
        self.guild_id = guild_id
        self.key = key
        self.multiple = multiple

    async def callback(self, interaction: discord.Interaction):
        ids = [int(v) for v in self.values]
        if self.multiple:
            self.cog.bot.guild_config[self.guild_id][self.key] = ids
        else:
            self.cog.bot.guild_config[self.guild_id][self.key] = ids[0]
        self.cog.save_config()
        await interaction.response.send_message(f"✅ {self.key.replace('_',' ').title()} set.", ephemeral=True)
        self.view.stop()

# true/false buttons
class ToggleView(discord.ui.View):
    def __init__(self, cog, guild_id, key):
        super().__init__(timeout=None)
        self.cog = cog
        self.guild_id = guild_id
        self.key = key

    @discord.ui.button(label="Enable", style=discord.ButtonStyle.green)
    async def enable(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.cog.bot.guild_config[self.guild_id][self.key] = True
        self.cog.save_config()
        await interaction.response.send_message(f"✅ {self.key.replace('_',' ').title()} enabled", ephemeral=True)
        self.stop()

    @discord.ui.button(label="Disable", style=discord.ButtonStyle.red)
    async def disable(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.cog.bot.guild_config[self.guild_id][self.key] = False
        self.cog.save_config()
        await interaction.response.send_message(f"✅ {self.key.replace('_',' ').title()} disabled", ephemeral=True)
        self.stop()

# level roles selection
class LevelRoleSetupView(discord.ui.View):
    def __init__(self, cog, guild_id):
        super().__init__(timeout=None)
        self.cog = cog
        self.guild_id = guild_id
        self.add_item(LevelRoleSelect(cog, guild_id))

class LevelRoleSelect(discord.ui.Select):
    def __init__(self, cog, guild_id):
        guild = cog.bot.get_guild(int(guild_id))
        options = [discord.SelectOption(label=r.name, value=str(r.id)) for r in guild.roles if not r.is_default()]
        super().__init__(placeholder="Pick a role to assign to a level...", options=options)
        self.cog = cog
        self.guild_id = guild_id

    async def callback(self, interaction: discord.Interaction):
        role_id = int(self.values[0])
        await interaction.response.send_message(
            "Enter the level number for this role in chat:", ephemeral=True
        )

        def check(m: discord.Message):
            return m.author.id == interaction.user.id and m.channel == interaction.channel and m.content.isdigit()

        msg = await self.cog.bot.wait_for("message", check=check)
        level = msg.content
        self.cog.bot.guild_config[self.guild_id]["level_roles"][level] = role_id
        self.cog.save_config()
        await interaction.followup.send(f"✅ Role <@&{role_id}> assigned to level {level}", ephemeral=True)

# cog setup
async def setup(bot: commands.Bot):
    await bot.add_cog(Config(bot))