from redbot.core import commands, Config
import discord

class Character(commands.Cog):
    """Character management for the RPG cog"""

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=1234567890, force_registration=True)
        self.config.register_user(characters={})  # Default to an empty dictionary of characters

    async def get_user_data(self, user):
        """Ensures user data exists and initializes it if not."""
        user_data = await self.config.user(user).all()
        if not user_data.get("characters"):
            await self.config.user(user).set({"characters": {}})
            user_data = await self.config.user(user).all()
        return user_data

    @commands.command()
    async def create(self, ctx):
        """Interactively create a new character."""
        await ctx.send("What would you like your character's name to be?")
        name = await self.bot.wait_for("message", check=lambda m: m.author == ctx.author)
        
        await ctx.send("What is your character's race?")
        race = await self.bot.wait_for("message", check=lambda m: m.author == ctx.author)
        
        await ctx.send("What is your character's gender?")
        gender = await self.bot.wait_for("message", check=lambda m: m.author == ctx.author)
        
        await ctx.send("Would you like to provide a backstory? (Type 'none' for no backstory)")
        backstory = await self.bot.wait_for("message", check=lambda m: m.author == ctx.author)

        character_data = {
            "name": name.content,
            "race": race.content,
            "gender": gender.content,
            "backstory": backstory.content if backstory.content != "none" else "No backstory",
            "level": 1,
            "health": 100,
            "strength": 10,
            "experience": 0,
        }

        user_data = await self.get_user_data(ctx.author)
        user_data["characters"][name.content] = character_data
        await self.config.user(ctx.author).set(user_data)

        await ctx.send(f"Character {name.content} created successfully!")

    @commands.command()
    async def list(self, ctx):
        """List all your characters."""
        user_data = await self.get_user_data(ctx.author)
        characters = user_data["characters"]
        
        if not characters:
            await ctx.send("You don't have any characters yet!")
            return
        
        character_list = "\n".join([f"{name} (Level {char['level']})" for name, char in characters.items()])
        await ctx.send(f"Your characters:\n{character_list}")

    @commands.command()
    async def info(self, ctx, name: str):
        """View your character's information."""
        user_data = await self.get_user_data(ctx.author)
        characters = user_data["characters"]
        
        if name not in characters:
            await ctx.send(f"You don't have a character named {name}.")
            return
        
        char = characters[name]
        embed = discord.Embed(title=f"{name}'s Character Info", color=discord.Color.green())
        embed.add_field(name="Name", value=char["name"], inline=False)
        embed.add_field(name="Race", value=char["race"], inline=False)
        embed.add_field(name="Gender", value=char["gender"], inline=False)
        embed.add_field(name="Backstory", value=char["backstory"], inline=False)
        embed.add_field(name="Level", value=char["level"], inline=True)
        embed.add_field(name="Health", value=char["health"], inline=True)
        embed.add_field(name="Strength", value=char["strength"], inline=True)
        embed.add_field(name="Experience", value=char["experience"], inline=True)

        await ctx.send(embed=embed)
