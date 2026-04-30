"""
Discord Bot Learning Project
----------------------------
This file is organized so you can come back later and reuse examples.

Included examples:
1. Secure token loading with .env
2. Bot setup and intents
3. Slash command syncing
4. Message events
5. Reaction roles
6. Basic slash commands
7. Embeds
8. Buttons
9. Dropdown/select menus

Project files you should have:
- main.py
- .env
- .gitignore
- requirements.txt

.env example:
DISCORD_TOKEN=your_bot_token_here

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

# Loads variables from the .env file into this Python program.
load_dotenv()

# Gets the bot token from .env instead of hardcoding it in the code.
TOKEN = os.getenv("DISCORD_TOKEN")

# Gives a clear error if the token is missing.
if TOKEN is None:
    raise ValueError("DISCORD_TOKEN not found. Check your .env file.")

# Your Discord server ID.
# Guild/server commands sync faster than global slash commands while testing.
GUILD_ID_NUMBER = 820679864872992779
GUILD = discord.Object(id=GUILD_ID_NUMBER)

# Emoji -> role name map for reaction roles.
# These role names must match your Discord server roles exactly.
REACTION_ROLE_MAP = {
    "⚪": "Member",
    "🔵": "Pirate",
    "🟢": "Blocky Dude",
    "🔴": "Finals",
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
        # Important: this resets when the bot restarts.
        # Later, you can save this ID in a text file, JSON file, or database.
        self.color_role_message_id = None

        # Stops slash commands from syncing over and over if on_ready runs again.
        self.synced = False

    async def on_ready(self):
        """Runs when the bot successfully logs in."""
        print(f"Logged in as {self.user}!")

        # Prevents repeated syncing if Discord reconnects the bot.
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
        # If someone sends a message that starts with "hello", the bot responds.
        if message.content.lower().startswith("hello"):
            await message.channel.send(f"Hey {message.author.mention}!")

        # Keeps regular prefix commands working if you add any !commands later.
        await self.process_commands(message)

    async def on_reaction_add(self, reaction, user):
        """Adds a role when a user reacts to the reaction role message."""

        # Ignore bot reactions.
        if user.bot:
            return

        guild = reaction.message.guild
        if guild is None:
            return

        # Only respond to reactions on the saved reaction role message.
        if reaction.message.id != self.color_role_message_id:
            return

        emoji = str(reaction.emoji)
        role_name = REACTION_ROLE_MAP.get(emoji)

        # Ignore emojis that are not in the reaction role map.
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

        # Ignore bot reactions.
        if user.bot:
            return

        guild = reaction.message.guild
        if guild is None:
            return

        # Only respond to reactions removed from the saved reaction role message.
        if reaction.message.id != self.color_role_message_id:
            return

        emoji = str(reaction.emoji)
        role_name = REACTION_ROLE_MAP.get(emoji)

        # Ignore emojis that are not in the reaction role map.
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

@client.tree.command(name="hello", description="Say hello!", guild=GUILD)
async def hello(interaction: discord.Interaction):
    """Simple slash command that replies with a greeting."""
    await interaction.response.send_message("Hi there!")


@client.tree.command(name="printer_demo", description="Repeats whatever you tell me to say.", guild=GUILD)
async def printer(interaction: discord.Interaction, text: str):
    """Repeats the text the user gives to the command."""
    await interaction.response.send_message(text)


# ============================================================
# 4. EMBED EXAMPLE
# ============================================================

@client.tree.command(name="embed_demo", description="Shows an example embed.", guild=GUILD)
async def embed_demo(interaction: discord.Interaction):
    """Shows how to create and send an embed."""

    embed = discord.Embed(
        title="I am a title",
        url="https://m.youtube.com/watch?v=d-pDGrl1jYw",
        description="I am the description",
        color=discord.Color.purple()
    )

    embed.set_thumbnail(
        url="https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fstatic.hudl.com%2Fusers%2Fprod%2F11378082_c473f95a4f06455abc68511ab42e1ad5.jpg&f=1&nofb=1&ipt=306dc51fe022a39feb4420b81f04b9e414aa4c405159750d760eebab7dfafde4"
    )

    embed.add_field(name="Field 1 Title", value="Field 1 description", inline=False)
    embed.add_field(name="Field 2 Title", value="Field 2 description", inline=True)
    embed.add_field(name="Field 3 Title", value="Field 3 description", inline=True)

    embed.set_footer(text="This is the footer")
    embed.set_author(name=interaction.user.name, icon_url=interaction.user.display_avatar.url)

    await interaction.response.send_message(embed=embed)


# ============================================================
# 5. BUTTON UI EXAMPLE
# ============================================================

class ButtonDemoView(discord.ui.View):
    """A View holds Discord UI components like buttons and dropdown menus."""

    @discord.ui.button(label="1st button", style=discord.ButtonStyle.blurple, emoji="1️⃣")
    async def button_callback1(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("You clicked the first button!", ephemeral=True)

    @discord.ui.button(label="2nd button", style=discord.ButtonStyle.red, emoji="2️⃣")
    async def button_callback2(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("You clicked the second button!", ephemeral=True)

    @discord.ui.button(label="3rd button", style=discord.ButtonStyle.green, emoji="3️⃣")
    async def button_callback3(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("You clicked the third button!", ephemeral=True)


@client.tree.command(name="button_demo", description="Displays buttons.", guild=GUILD)
async def button_demo(interaction: discord.Interaction):
    """Sends a message with clickable buttons."""
    await interaction.response.send_message("Choose a button:", view=ButtonDemoView())


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
                description="This is the first option",
                emoji="🖐"
            ),
            discord.SelectOption(
                label="Option 2",
                value="option_2",
                description="This is the second option",
            ),
            discord.SelectOption(
                label="Option 3",
                value="option_3",
                description="This is the third option",
            ),
        ]

        super().__init__(
            placeholder="Please choose an option:",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        """Runs after the user chooses an option from the dropdown."""

        selected_value = self.values[0]

        if selected_value == "option_1":
            await interaction.response.send_message("You picked option 1", ephemeral=True)

        elif selected_value == "option_2":
            await interaction.response.send_message("You picked option 2", ephemeral=True)

        elif selected_value == "option_3":
            await interaction.response.send_message("You picked option 3", ephemeral=True)


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

@client.tree.command(name="reaction_roles_demo", description="Create a message that lets users pick a role.", guild=GUILD)
async def reaction_roles(interaction: discord.Interaction):
    """Creates a reaction role message and adds the role emojis to it."""

    # Only admins should be able to create the reaction role message.
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message(
            "You must be an admin to run this command!",
            ephemeral=True
        )
        return

    # Defers the command response so Discord does not time out while reactions are added.
    await interaction.response.defer()

    description = (
        "React to this message to get your role!\n\n"
        "⚪ Member\n"
        "🔵 Pirate\n"
        "🟢 Blocky Dude\n"
        "🔴 Finals\n"
    )

    embed = discord.Embed(
        title="Pick your role",
        description=description,
        color=discord.Color.purple()
    )

    # Sends the embed and returns the sent message.
    # wait=True is needed so we can add reactions to the message.
    message = await interaction.followup.send(embed=embed, wait=True)

    # Adds every emoji from the reaction role map to the message.
    for emoji in REACTION_ROLE_MAP.keys():
        await message.add_reaction(emoji)

    # Saves the message ID so the reaction events know which message to watch.
    # This only lasts until the bot restarts.
    client.color_role_message_id = message.id

    await interaction.followup.send("Role message created!", ephemeral=True)


# ============================================================
# 8. RUN THE BOT
# ============================================================

client.run(TOKEN)
