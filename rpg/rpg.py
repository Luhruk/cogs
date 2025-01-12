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

    @commands.command()
    async def createchar(self, ctx, name: str, race: str, gender: str, image_url: str = None, *, backstory: str = "None"):
        """
        Create your RPG character.

        Parameters:
        - name: The name of your character.
        - race: The race of your character (e.g., Human, Elf, Orc).
        - gender: The gender of your character (e.g., Male, Female, Non-binary).
        - image_url: (Optional) A URL to an image representing your character.
        - backstory: (Optional) A backstory for your character.
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

    @commands.command()
    async def charinfo(self, ctx):
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

    @commands.command()
    async def setactive(self, ctx, index: int):
        """
        Set your active character by choosing its index.
        """
        characters = await self.config.user(ctx.author).characters()
        
        if index < 1 or index > len(characters):
            await ctx.send(f"Invalid index! You have {len(characters)} characters.")
            return

        await self.config.user(ctx.author).active_character.set(index - 1)
        await ctx.send(f"Character {characters[index - 1]['name']} is now your active character!")

    @commands.command()
    async def deletechar(self, ctx, index: int):
        """
        Delete a specific character by index.
        """
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
