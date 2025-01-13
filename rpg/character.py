from redbot.core import commands, Config
import discord

class Character(commands.Cog):
    """Character-related commands for RPG"""

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=1234567890, force_registration=True)
        self.config.register_user(characters=[])

    @commands.command()
    async def create(self, ctx):
        """Interactively create a new character."""
        await ctx.send("What would you like your character's name to be?")
        name = await self.bot.wait_for("message", check=lambda m: m.author == ctx.author)

        await ctx.send(f"Your character's name is {name.content}. What is your character's race?")
        race = await self.bot.wait_for("message", check=lambda m: m.author == ctx.author)

        await ctx.send(f"Your character is a {race.content}. What is your character's gender?")
        gender = await self.bot.wait_for("message", check=lambda m: m.author == ctx.author)

        await ctx.send(f"Your character is {gender.content}. What is your character's backstory?")
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

        user_data = await self.config.user(ctx.author).all()
        if "characters" not in user_data:
            user_data["characters"] = []

        user_data["characters"].append(character)
        await self.config.user(ctx.author).set(user_data)

        await ctx.send(f"Character created!\nName: {name.content}\nRace: {race.content}\nGender: {gender.content}\nBackstory: {backstory.content}")

    @commands.command()
    async def list(self, ctx):
        """List all your characters."""
        user_data = await self.config.user(ctx.author).all()

        # Ensure user data is initialized
        if "characters" not in user_data:
            user_data["characters"] = []
            await self.config.user(ctx.author).set(user_data)

        if not user_data["characters"]:
            await ctx.send("You don't have any characters yet! Use `.rpg char create` to create one.")
            return

        embed = discord.Embed(title=f"{ctx.author.display_name}'s Characters", color=discord.Color.green())
        for i, character in enumerate(user_data["characters"]):
            embed.add_field(name=f"Character {i+1}: {character['name']}", value=f"Level: {character['level']}", inline=False)

        await ctx.send(embed=embed)

    @commands.command()
    async def info(self, ctx):
        """View your character's information."""
        user_data = await self.config.user(ctx.author).all()

        # Ensure user data is initialized
        if "characters" not in user_data or not user_data["characters"]:
            await ctx.send("You don't have any characters yet! Use `.rpg char create` to create one.")
            return

        character = user_data["characters"][-1]  # Display the most recent character
        embed = discord.Embed(title=f"{ctx.author.display_name}'s Character", color=discord.Color.green())
        embed.add_field(name="Name", value=character["name"], inline=False)
        embed.add_field(name="Race", value=character["race"], inline=False)
        embed.add_field(name="Gender", value=character["gender"], inline=False)
        embed.add_field(name="Backstory", value=character["backstory"], inline=False)
        embed.add_field(name="Level", value=character["level"], inline=True)
        embed.add_field(name="Health", value=character["health"], inline=True)
        embed.add_field(name="Strength", value=character["strength"], inline=True)
        embed.add_field(name="Experience", value=character["experience"], inline=True)

        await ctx.send(embed=embed)

    @commands.command()
    async def delete(self, ctx, character_name: str):
        """Delete a specific character."""
        user_data = await self.config.user(ctx.author).all()

        if "characters" not in user_data or not user_data["characters"]:
            await ctx.send("You don't have any characters to delete.")
            return

        character = next((c for c in user_data["characters"] if c["name"].lower() == character_name.lower()), None)
        if not character:
            await ctx.send(f"No character found with the name {character_name}.")
            return

        user_data["characters"].remove(character)
        await self.config.user(ctx.author).set(user_data)

        await ctx.send(f"Character {character_name} has been deleted.")
