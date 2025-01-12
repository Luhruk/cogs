from redbot.core import commands, Config
import discord

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

    @commands.group()
    async def char(self, ctx):
        """Character-related commands."""
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @char.command()
    async def create(self, ctx, name: str, race: str, gender: str, image_url: str = None, *, backstory: str = "None"):
        """
        Create your RPG character.
        """
        characters = await self.config.user(ctx.author).characters()
        
        # Check if a character already exists
        character = {
            "name": name,
            "race": race.capitalize(),
            "gender": gender.capitalize(),
            "backstory": backstory,
            "image_url": image_url,
            "level": 1,
            "health": 100,
            "strength": 10,
            "experience": 0,
        }

        characters.append(character)
        await self.config.user(ctx.author).characters.set(characters)

        await ctx.send(f"Character created! You now have {len(characters)} characters.")

    @char.command()
    async def info(self, ctx):
        """View your active character's information."""
        characters = await self.config.user(ctx.author).characters()
        active_character_index = await self.config.user(ctx.author).active_character()

        if active_character_index is None or active_character_index >= len(characters):
            await ctx.send("You don't have an active character! Use `[p]setactive` to choose one.")
            return

        character = characters[active_character_index]

        embed = discord.Embed(title=f"{ctx.author.display_name}'s Character", color=discord.Color.green())
        embed.add_field(name="Name", value=character["name"], inline=False)
        embed.add_field(name="Race", value=character["race"], inline=False)
        embed.add_field(name="Gender", value=character["gender"], inline=False)
        embed.add_field(name="Backstory", value=character["backstory"], inline=False)
        embed.add_field(name="Level", value=character["level"] , inline=True)
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
