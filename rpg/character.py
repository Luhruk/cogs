from redbot.core import commands, Config
import discord

class CharacterCommands(commands.Cog):
    """Character-related commands."""

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=1234567890, force_registration=True)
        self.config.register_user(characters=[])

    async def create(self, ctx):
        """Create a new character interactively."""
        await ctx.send("What would you like your character name to be?")
        name = await self.bot.wait_for("message", check=lambda m: m.author == ctx.author)
        
        await ctx.send("What is your race?")
        race = await self.bot.wait_for("message", check=lambda m: m.author == ctx.author)
        
        await ctx.send("What is your gender?")
        gender = await self.bot.wait_for("message", check=lambda m: m.author == ctx.author)
        
        await ctx.send("Provide a backstory for your character:")
        backstory = await self.bot.wait_for("message", check=lambda m: m.author == ctx.author)
        
        character = {
            "name": name.content,
            "race": race.content,
            "gender": gender.content,
            "backstory": backstory.content,
            "level": 1,
            "health": 100,
            "strength": 10,
            "experience": 0,
        }

        user_data = await self.config.user(ctx.author).characters()
        user_data.append(character)
        await self.config.user(ctx.author).characters.set(user_data)

        await ctx.send(f"Character created!\nName: **{name.content}**\nRace: **{race.content}**\nGender: **{gender.content}**\nBackstory: **{backstory.content}**")

    async def info(self, ctx):
        """View your character's information."""
        characters = await self.config.user(ctx.author).characters()
        if not characters:
            await ctx.send("You don't have any characters yet! Use `[p]char create` to create one.")
            return

        embed = discord.Embed(title=f"{ctx.author.display_name}'s Characters", color=discord.Color.green())
        for character in characters:
            embed.add_field(name=f"{character['name']}", value=f"Level: {character['level']} | Health: {character['health']} | Strength: {character['strength']}", inline=False)

        await ctx.send(embed=embed)

    async def list(self, ctx):
        """List all of your characters."""
        characters = await self.config.user(ctx.author).characters()
        if not characters:
            await ctx.send("You don't have any characters yet! Use `[p]char create` to create one.")
            return

        embed = discord.Embed(title=f"{ctx.author.display_name}'s Characters", color=discord.Color.green())
        for character in characters:
            embed.add_field(name=f"{character['name']}", value=f"Level: {character['level']} | Health: {character['health']} | Strength: {character['strength']}", inline=False)

        await ctx.send(embed=embed)

    async def delete(self, ctx, character_name: str):
        """Delete a specific character."""
        characters = await self.config.user(ctx.author).characters()
        character = next((char for char in characters if char["name"].lower() == character_name.lower()), None)
        if not character:
            await ctx.send(f"No character named {character_name} found.")
            return

        characters.remove(character)
        await self.config.user(ctx.author).characters.set(characters)
        await ctx.send(f"Character {character_name} has been deleted.")
