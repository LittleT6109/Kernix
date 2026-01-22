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
            discord.SelectOption(label="Toggle Welcome Messages", value="toggle_welcome"),
            discord.SelectOption(label="Set Welcome Channel", value="set_welcome_channel"),
            discord.SelectOption(label="Set Welcome Messages", value="set_welcome_messages"),
            discord.SelectOption(label="Toggle Autorole", value="toggle_autorole"),
            discord.SelectOption(label="Set Autorole", value="set_autorole"),
            discord.SelectOption(label="Toggle Logging", value="toggle_logging"),
            discord.SelectOption(label="Set Log Channel", value="set_log_channel"),
            discord.SelectOption(label="Toggle Mod Action Logging", value="toggle_mod_logging"),
            discord.SelectOption(label="Set Mod Action Log Channel", value="set_mod_channel"),
            discord.SelectOption(label="Set Mod Roles", value="set_mod_roles"),
            discord.SelectOption(label="Toggle Leveling", value="toggle_leveling"),
            discord.SelectOption(label="Set Level Roles", value="set_level_roles"),
        ]

        super().__init__(placeholder="Choose an option...", options=options, min_values=1, max_values=1)
        self.cog = cog
        self.guild = guild

    async def callback(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        if guild_id not in self.cog.bot.guild_config:
            self.cog.bot.guild_config[guild_id] = {
                "welcome_status": False,
                "welcome_channel": None,
                "welcome_messages": [],
                "autorole_status": False,
                "autorole": None,
                "logging_status": False,
                "log_channel": None,
                "mod_logging_status": False,
                "mod_channel": None,
                "mod_roles": [],
                "leveling_status": False,
                "level_roles": {}
            }
            self.cog.save_config()

        choice = self.values[0]

        if choice == "toggle_welcome":
            await interaction.response.send_message(
                "Toggle Welcomes:",
                view=ToggleView(self.cog, guild_id, "welcome_status"),
                ephemeral=True
            )
        elif choice == "set_welcome_channel":
            await interaction.response.send_message(
                "Select the welcome channel:",
                view=ChannelSelectView(self.cog, guild_id, key="welcome_channel"),
                ephemeral=True
            )
        elif choice == "set_welcome_messages":
            await interaction.response.send_modal(
                ConfigModal(
                self.cog,
                guild_id,
                title="Welcome Messages",
                label="One per line, use {user} to mention the user",
                placeholder="Hello there {user}!",
                step="welcome_messages"
            )
        )
        elif choice == "toggle_autorole":
            await interaction.response.send_message(
                "Toggle Autorole:",
                view=ToggleView(self.cog, guild_id, "autorole_status"),
                ephemeral=True
            )
        elif choice == "set_autorole":
            await interaction.response.send_message(
                "Select the autorole:",
                view=RoleSelectView(self.cog, guild_id, "autorole"),
                ephemeral=True
            )
        elif choice == "toggle_logging":
            await interaction.response.send_message(
                "Toggle logging:",
                view=ToggleView(self.cog, guild_id, "logging_status"),
                ephemeral=True
            )
        elif choice == "set_log_channel":
            await interaction.response.send_message(
                "Select the log channel:",
                view=ChannelSelectView(self.cog, guild_id, key="log_channel"),
                ephemeral=True
            )
        elif choice == "toggle_mod_logging":
            await interaction.response.send_message(
                "Toggle mod action logging:",
                view=ToggleView(self.cog, guild_id, "mod_logging_status"),
                ephemeral=True
            )
        elif choice == "set_mod_channel":
            await interaction.response.send_message(
                "Select the log channel",
                view=ChannelSelectView(self.cog, guild_id, "mod_channel"),
                ephemeral=True
            )
        elif choice == "set_mod_roles":
            await interaction.response.send_message(
                "Select mod roles:",
                view=RoleSelectView(self.cog, guild_id, "mod_roles", multiple=True),
                ephemeral=True
            )
        elif choice == "toggle_leveling":
            await interaction.response.send_message(
                "Toggle leveling system:",
                view=ToggleView(self.cog, guild_id, "leveling_status"),
                ephemeral=True
            )
        elif choice == "set_level_roles":
            await interaction.response.send_modal(
                ConfigModal(
                    self.cog,
                    guild_id,
                    title="Level Roles",
                    label="One per line, format: <level>: <role mention>",
                    placeholder="5: @Image Perms",
                    step="level_roles"
                )
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
        options = options[:25]
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

class ConfigModal(discord.ui.Modal):
    def __init__(self, cog, guild_id, *, title, label, placeholder, step):
        super().__init__(title=title)
        self.cog = cog
        self.guild_id = guild_id
        self.step = step

        self.messages = discord.ui.TextInput(
            label=label,
            style=discord.TextStyle.paragraph,
            placeholder=placeholder
        )
        self.add_item(self.messages)

    async def on_submit(self, interaction: discord.Interaction):
        value = self.messages.value.strip()

        if value.lower() == "skip":
            self.cog.bot.guild_config[self.guild_id][self.step] = [] if self.step == "welcome_messages" else {}
            saved_count = 0
        else:
            lines = value.splitlines()
            if self.step == "welcome_messages":
                self.cog.bot.guild_config[self.guild_id][self.step] = lines
                saved_count = len(lines)
            elif self.step == "level_roles":
                data = {}
                for line in lines:
                    if ":" not in line:
                        continue
                    level, role = line.split(":", 1)

                    role_id = int(role.strip().replace("<@&", "").replace(">", ""))
                    data[int(level.strip())] = role_id

                self.cog.bot.guild_config[self.guild_id][self.step] = data
                saved_count = len(data)

        self.cog.save_config()

        await interaction.response.send_message(
            f"✅ Saved {saved_count} entries for {self.step.replace('_',' ')}.",
            ephemeral=True
        )

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
        options = options[:25]
        super().__init__(placeholder="Pick role(s)...", options=options, min_values=1, max_values=len(options) if multiple and options else 1)
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

# cog setup
async def setup(bot: commands.Bot):
    await bot.add_cog(Config(bot))