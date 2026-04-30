"""
Discord Bot Demo
----------------
A beginner-friendly Discord bot built with discord.py.

Features included:
1. Secure token loading with .env.example
2. Slash command syncing
3. Basic slash commands
4. Embed messages
5. Button interactions
6. Dropdown/select menus
7. Reaction roles

Project files:
- main.py
- .env.example
- .gitignore
- requirements.txt
- .env.example.example

.env.example example:
DISCORD_TOKEN=your_discord_bot_token_here
GUILD_ID=your_discord_server_id_here

requirements.txt example:
discord.py
python-dotenv
"""

import os

import discord
from discord.ext import commands
from dotenv import load_dotenv


# ============================================================
# 1. CONFIG / CONSTANTS
# ============================================================

# Loads variables from the .env.example file.
load_dotenv()

# Reads private values from the environment instead of hardcoding them.
TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = os.getenv("GUILD_ID")

# Gives clear errors if required environment variables are missing.
if TOKEN is None:
    raise ValueError("DISCORD_TOKEN not found. Check your .env.example file.")

if GUILD_ID is None:
    raise ValueError("GUILD_ID not found. Check your .env.example file.")

# Converts the guild/server ID from text to an integer.
GUILD_ID_NUMBER = int(GUILD_ID)
GUILD = discord.Object(id=GUILD_ID_NUMBER)

# Emoji -> role name map for reaction roles.
# These role names are generic for the public demo version.
# Make sure these roles exist in your Discord server if you test this feature.
REACTION_ROLE_MAP = {
    "🔵": "Blue Team",
    "🟢": "Green Team",
    "🔴": "Red Team",
}


# ============================================================
# 2. BOT CLASS / EVENTS
# ============================================================

class Client(commands.Bot):
    """Custom bot class that stores the bot setup and event listeners."""

    def __init__(self):
        # Intents decide which Discord events your bot is allowed to receive.
        intents = discord.Intents.default()
        intents.message_content = True  # Needed to read normal message text.
        intents.reactions = True        # Needed for reaction role events.
        intents.guilds = True           # Needed for server/guild info.
        intents.members = True          # Needed to manage/read member info.

        super().__init__(command_prefix="!", intents=intents)

        # Stores the ID of the reaction role message after it is created.
        # Note: this resets when the bot restarts.
        # A production bot should save this ID in a file or database.
        self.reaction_role_message_id = None

        # Prevents slash commands from syncing repeatedly if on_ready runs again.
        self.synced = False

    async def on_ready(self):
        """Runs when the bot successfully logs in."""
        print(f"Logged in as {self.user}!")

        if self.synced:
            return

        try:
            # Syncs slash commands to one server for faster testing.
            synced = await self.tree.sync(guild=GUILD)
            print(f"Synced {len(synced)} commands to guild {GUILD_ID_NUMBER}")
            self.synced = True

        except Exception as e:
            print(f"Error syncing commands: {e}")

    async def on_message(self, message):
        """Runs whenever the bot sees a message in a server channel."""

        # Prevents the bot from replying to itself.
        if message.author == self.user:
            return

        # Basic message event example.
        if message.content.lower().startswith("hello"):
            await message.channel.send(f"Hello, {message.author.mention}!")

        # Keeps regular prefix commands working if they are added later.
        await self.process_commands(message)

    async def on_reaction_add(self, reaction, user):
        """Adds a role when a user reacts to the reaction role message."""

        if user.bot:
            return

        guild = reaction.message.guild
        if guild is None:
            return

        # Only respond to reactions on the saved reaction role message.
        if reaction.message.id != self.reaction_role_message_id:
            return

        emoji = str(reaction.emoji)
        role_name = REACTION_ROLE_MAP.get(emoji)

        if role_name is None:
            return

        role = discord.utils.get(guild.roles, name=role_name)

        if role is None:
            print(f"Role not found: {role_name}")
            return

        try:
            await user.add_roles(role)
            print(f"Assigned {role_name} to {user}")

        except discord.Forbidden:
            print(f"Missing permission to assign role: {role_name}")

    async def on_reaction_remove(self, reaction, user):
        """Removes a role when a user removes their reaction."""

        if user.bot:
            return

        guild = reaction.message.guild
        if guild is None:
            return

        # Only respond to reactions removed from the saved reaction role message.
        if reaction.message.id != self.reaction_role_message_id:
            return

        emoji = str(reaction.emoji)
        role_name = REACTION_ROLE_MAP.get(emoji)

        if role_name is None:
            return

        role = discord.utils.get(guild.roles, name=role_name)

        if role is None:
            print(f"Role not found: {role_name}")
            return

        try:
            await user.remove_roles(role)
            print(f"Removed {role_name} from {user}")

        except discord.Forbidden:
            print(f"Missing permission to remove role: {role_name}")


# Creates the bot object.
client = Client()


# ============================================================
# 3. BASIC SLASH COMMANDS
# ============================================================

@client.tree.command(name="hello", description="Say hello.", guild=GUILD)
async def hello(interaction: discord.Interaction):
    """Simple slash command that replies with a greeting."""
    await interaction.response.send_message("Hello! Thanks for trying the bot.")


@client.tree.command(name="printer_demo", description="Repeats the text you provide.", guild=GUILD)
async def printer(interaction: discord.Interaction, text: str):
    """Repeats the text the user gives to the command."""
    await interaction.response.send_message(text)


# ============================================================
# 4. EMBED EXAMPLE
# ============================================================

@client.tree.command(name="embed_demo", description="Shows an example embed.", guild=GUILD)
async def embed_demo(interaction: discord.Interaction):
    """Shows how to create and send a professional-looking embed."""

    embed = discord.Embed(
        title="Discord Bot Demo",
        description="This is an example embed created with discord.py.",
        color=discord.Color.blue()
    )

    embed.add_field(
        name="Feature 1",
        value="Slash commands allow users to interact with the bot using Discord's command menu.",
        inline=False
    )

    embed.add_field(
        name="Feature 2",
        value="Embeds can organize information in a clean, readable format.",
        inline=False
    )

    embed.add_field(
        name="Feature 3",
        value="Buttons, dropdowns, and reactions can make the bot more interactive.",
        inline=False
    )

    embed.set_footer(text="Built with Python and discord.py")
    embed.set_author(
        name=interaction.user.name,
        icon_url=interaction.user.display_avatar.url
    )

    await interaction.response.send_message(embed=embed)


# ============================================================
# 5. BUTTON UI EXAMPLE
# ============================================================

class ButtonDemoView(discord.ui.View):
    """A View holds Discord UI components like buttons and dropdown menus."""

    @discord.ui.button(label="First", style=discord.ButtonStyle.blurple, emoji="1️⃣")
    async def button_callback1(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("You selected the first button.", ephemeral=True)

    @discord.ui.button(label="Second", style=discord.ButtonStyle.green, emoji="2️⃣")
    async def button_callback2(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("You selected the second button.", ephemeral=True)

    @discord.ui.button(label="Third", style=discord.ButtonStyle.gray, emoji="3️⃣")
    async def button_callback3(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("You selected the third button.", ephemeral=True)


@client.tree.command(name="button_demo", description="Displays interactive buttons.", guild=GUILD)
async def button_demo(interaction: discord.Interaction):
    """Sends a message with clickable buttons."""
    await interaction.response.send_message("Choose one of the buttons below:", view=ButtonDemoView())


# ============================================================
# 6. DROPDOWN / SELECT MENU UI EXAMPLE
# ============================================================

class DemoMenu(discord.ui.Select):
    """Dropdown menu with three selectable options."""

    def __init__(self):
        options = [
            discord.SelectOption(
                label="Option 1",
                value="option_1",
                description="Select the first demo option.",
                emoji="1️⃣"
            ),
            discord.SelectOption(
                label="Option 2",
                value="option_2",
                description="Select the second demo option.",
                emoji="2️⃣"
            ),
            discord.SelectOption(
                label="Option 3",
                value="option_3",
                description="Select the third demo option.",
                emoji="3️⃣"
            ),
        ]

        super().__init__(
            placeholder="Choose an option:",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        """Runs after the user chooses an option from the dropdown."""

        selected_value = self.values[0]

        if selected_value == "option_1":
            await interaction.response.send_message("You selected option 1.", ephemeral=True)

        elif selected_value == "option_2":
            await interaction.response.send_message("You selected option 2.", ephemeral=True)

        elif selected_value == "option_3":
            await interaction.response.send_message("You selected option 3.", ephemeral=True)


class MenuDemoView(discord.ui.View):
    """View that holds the dropdown menu."""

    def __init__(self):
        super().__init__()
        self.add_item(DemoMenu())


@client.tree.command(name="menu_demo", description="Displays a dropdown menu.", guild=GUILD)
async def menu_demo(interaction: discord.Interaction):
    """Sends a message with a dropdown menu."""
    await interaction.response.send_message("Please choose an option:", view=MenuDemoView())


# ============================================================
# 7. REACTION ROLE COMMAND
# ============================================================

@client.tree.command(
    name="reaction_roles_demo",
    description="Creates a message that lets users pick a demo role.",
    guild=GUILD
)
async def reaction_roles(interaction: discord.Interaction):
    """Creates a reaction role message and adds role emojis to it."""

    # Only admins should be able to create the reaction role message.
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message(
            "You must be an administrator to run this command.",
            ephemeral=True
        )
        return

    # Defers the command response so Discord does not time out while reactions are added.
    await interaction.response.defer()

    description = (
        "React to this message to receive a demo role.\n\n"
        "🔵 Blue Team\n"
        "🟢 Green Team\n"
        "🔴 Red Team\n"
    )

    embed = discord.Embed(
        title="Choose a Demo Role",
        description=description,
        color=discord.Color.blue()
    )

    # Sends the embed and returns the sent message.
    # wait=True is needed so reactions can be added to the message.
    message = await interaction.followup.send(embed=embed, wait=True)

    # Adds every emoji from the reaction role map to the message.
    for emoji in REACTION_ROLE_MAP.keys():
        await message.add_reaction(emoji)

    # Saves the message ID so the reaction events know which message to watch.
    # This only lasts until the bot restarts.
    client.reaction_role_message_id = message.id

    await interaction.followup.send("Reaction role message created.", ephemeral=True)


# ============================================================
# 8. RUN THE BOT
# ============================================================

client.run(TOKEN)