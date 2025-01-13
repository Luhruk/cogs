from redbot.core import commands, Config
import discord
import asyncio

class RPG(commands.Cog):
    """A role-playing game cog"""

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=1234567890, force_registration=True)
        default_user = {
            "characters": [],  # Stores a list of character data
            "active_character": None,  # The active character index
        }
        self.config.register_user(**default_user)

    @commands.group(invoke_without_command=True)
    async def char(self, ctx):
        """Character-related commands."""
        await ctx.send_help(ctx.command)

    @char.command()
    async def create(self, ctx):
        """Interactive character creation."""
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        await ctx.send("What would you like your character's name to be?")
        try:
            name_msg = await self.bot.wait_for("message", check=check, timeout=60)
            name = name_msg.content
        except asyncio.TimeoutError:
            await ctx.send("You took too long to respond! Please try again.")
            return

        await ctx.send("What is your character's race? (e.g., Human, Elf, Orc)")
        try:
            race_msg = await self.bot.wait_for("message", check=check, timeout=60)
            race = race_msg.content.capitalize()
        except asyncio.TimeoutError:
            await ctx.send("You took too long to respond! Please try again.")
            return

        await ctx.send("What is your character's gender? (e.g., Male, Female, Non-binary)")
        try:
            gender_msg = await self.bot.wait_for("message", check=check, timeout=60)
            gender = gender_msg.content.capitalize()
        except asyncio.TimeoutError:
            await ctx.send("You took too long to respond! Please try again.")
            return

        await ctx.send("Would you like to provide an image URL for your character? (Type 'skip' to skip this step)")
        try:
            image_url_msg = await self.bot.wait_for("message", check=check, timeout=60)
            image_url = image_url_msg.content if image_url_msg.content.lower() != "skip" else None
        except asyncio.TimeoutError:
            await ctx.send("You took too long to respond! Please try again.")
            return

        await ctx.send("Finally, provide a backstory for your character. (Type 'none' for no backstory)")
        try:
            backstory_msg = await self.bot.wait_for("message", check=check, timeout=120)
            backstory = backstory_msg.content if backstory_msg.content.lower() != "none" else "None"
        except asyncio.TimeoutError:
            await ctx.send("You took too long to respond! Please try again.")
            return

        # Create the character
        characters = await self.config.user(ctx.author).characters()
        character = {
            "name": name,
            "race": race,
            "gender": gender,
            "backstory": backstory,
            "image_url": image_url,
            "level": 1,
            "health": 100,
            "strength": 10,
            "experience": 0,
        }

        characters.append(character)
        await self.config.user(ctx.author).characters.set(characters)

        await ctx.send(
            f"Character created!\n"
            f"Name: **{character['name']}**\n"
            f"Race: **{character['race']}**\n"
            f"Gender: **{character['gender']}**\n"
            f"Backstory: **{character['backstory']}**\n"
            f"Level: **{character['level']}**\n"
            f"Health: **{character['health']}**\n"
            f"Strength: **{character['strength']}**"
        )

    @char.command()
    async def info(self, ctx):
        """View your active character's information."""
        characters = await self.config.user(ctx.author).characters()
        active_character_index = await self.config.user(ctx.author).active_character()

        if active_character_index is None or active_character_index >= len(characters):
            await ctx.send("You don't have an active character! Use `[p]char setactive` to choose one.")
            return

        character = characters[active_character_index]

        embed = discord.Embed(title=f"{ctx.author.display_name}'s Character", color=discord.Color.green())
        embed.add_field(name="Name", value=character["name"], inline=False)
        embed.add_field(name="Race", value=character["race"], inline=False)
        embed.add_field(name="Gender", value=character["gender"], inline=False)
        embed.add_field(name="Backstory", value=character["backstory"], inline=False)
        embed.add_field(name="Level", value=character["level"], inline=True)
        embed.add_field(name="Health", value=character["health"], inline=True)
        embed.add_field(name="Strength", value=character["strength"], inline=True)
        embed.add_field(name="Experience", value=character["experience"], inline=True)

        if character.get("image_url"):
            embed.set_thumbnail(url=character["image_url"])

        await ctx.send(embed=embed)

    @char.command()
    async def setactive(self, ctx, index: int):
        """Set your active character by choosing its index."""
        characters = await self.config.user(ctx.author).characters()
        
        if index < 1 or index > len(characters):
            await ctx.send(f"Invalid index! You have {len(characters)} characters.")
            return

        await self.config.user(ctx.author).active_character.set(index - 1)
        await ctx.send(f"Character {characters[index - 1]['name']} is now your active character!")

    @char.command()
    async def delete(self, ctx, index: int):
        """Delete a specific character by index."""
        characters = await self.config.user(ctx.author).characters()

        if index < 1 or index > len(characters):
            await ctx.send(f"Invalid index! You have {len(characters)} characters.")
            return

        deleted_character = characters.pop(index - 1)
        await self.config.user(ctx.author).characters.set(characters)

        # If the deleted character was the active one, reset the active character
        active_character_index = await self.config.user(ctx.author).active_character()
        if active_character_index is not None and active_character_index >= index - 1:
            await self.config.user(ctx.author).active_character.set(None)

        await ctx.send(f"Character {deleted_character['name']} has been deleted.")

    @char.command()
    async def list(self, ctx):
        """List all your characters."""
        characters = await self.config.user(ctx.author).characters()

        if not characters:
            await ctx.send("You don't have any characters yet!")
            return

        character_list = "\n".join([f"{i+1}. {char['name']} ({char['race']}, {char['gender']}) - Level {char['level']}" for i, char in enumerate(characters)])
        await ctx.send(f"Your characters:\n{character_list}")
