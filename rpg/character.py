from redbot.core import commands, Config
import discord

class CharacterCommands:
    def __init__(self, bot, config):
        self.bot = bot
        self.config = config

    async def create(self, ctx):
        """Interactive character creation."""
        await ctx.send("What would you like your character's name to be?")
        name = await self.bot.wait_for('message', check=lambda m: m.author == ctx.author)
        
        await ctx.send("What is your character's race?")
        race = await self.bot.wait_for('message', check=lambda m: m.author == ctx.author)
        
        await ctx.send("What is your character's gender?")
        gender = await self.bot.wait_for('message', check=lambda m: m.author == ctx.author)
        
        await ctx.send("What is your character's backstory?")
        backstory = await self.bot.wait_for('message', check=lambda m: m.author == ctx.author)
        
        await ctx.send("Do you have an image URL for your character? (Leave blank for none)")
        image_url = await self.bot.wait_for('message', check=lambda m: m.author == ctx.author)
        image_url = image_url.content if image_url.content else None
        
        character = {
            "name": name.content,
            "race": race.content.capitalize(),
            "gender": gender.content.capitalize(),
            "backstory": backstory.content,
            "image_url": image_url,
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

        await ctx.send(f"Character created!\nName: {name.content}\nRace: {race.content}\nGender: {gender.content}\nBackstory: {backstory.content}\nLevel: 1")

    async def info(self, ctx):
        """View your active character's information."""
        user_data = await self.config.user(ctx.author).all()

        if not user_data.get("characters"):
            await ctx.send("You don't have any characters yet! Use `.rpg char create` to create one.")
            return

        active_character_index = user_data.get("active_character")
        if active_character_index is None or active_character_index >= len(user_data["characters"]):
            await ctx.send("You don't have an active character set. Use `.rpg char setactive` to set one.")
            return

        character = user_data["characters"][active_character_index]
        
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

    async def list(self, ctx):
        """List all your characters."""
        user_data = await self.config.user(ctx.author).all()

        if not user_data.get("characters"):
            await ctx.send("You don't have any characters yet! Use `.rpg char create` to create one.")
            return

        embed = discord.Embed(title=f"{ctx.author.display_name}'s Characters", color=discord.Color.green())
        for i, character in enumerate(user_data["characters"]):
            embed.add_field(name=f"Character {i+1}: {character['name']}", value=f"Level: {character['level']}", inline=False)

        await ctx.send(embed=embed)

    async def setactive(self, ctx, index: int):
        """Set your active character by choosing its index."""
        user_data = await self.config.user(ctx.author).all()

        if not user_data.get("characters"):
            await ctx.send("You don't have any characters yet! Use `.rpg char create` to create one.")
            return

        if index < 1 or index > len(user_data["characters"]):
            await ctx.send(f"Invalid index! Please choose a number between 1 and {len(user_data['characters'])}.")
            return

        user_data["active_character"] = index - 1
        await self.config.user(ctx.author).set(user_data)

        await ctx.send(f"Character {index} is now your active character.")

    async def delete(self, ctx, index: int):
        """Delete a specific character by index."""
        user_data = await self.config.user(ctx.author).all()

        if not user_data.get("characters"):
            await ctx.send("You don't have any characters yet! Use `.rpg char create` to create one.")
            return

        if index < 1 or index > len(user_data["characters"]):
            await ctx.send(f"Invalid index! Please choose a number between 1 and {len(user_data['characters'])}.")
            return

        deleted_character = user_data["characters"].pop(index - 1)
        await self.config.user(ctx.author).set(user_data)

        await ctx.send(f"Character {deleted_character['name']} has been deleted.")
