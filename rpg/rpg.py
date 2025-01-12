from redbot.core import commands, Config
import discord

class RPG(commands.Cog):
    """A role-playing game cog"""

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=1234567890, force_registration=True)
        default_user = {
            "character": None,  # Stores the character data
        }
        self.config.register_user(**default_user)

    @commands.command()
    async def createchar(self, ctx, name: str, race: str, gender: str, *, backstory: str = "None"):
        """
        Create your RPG character.

        Parameters:
        - name: The name of your character.
        - race: The race of your character (e.g., Human, Elf, Orc).
        - gender: The gender of your character (e.g., Male, Female, Non-binary).
        - backstory: (Optional) A backstory for your character.
        """
        async with self.config.user(ctx.author).character() as character:
            if character:
                await ctx.send("You already have a character! Use `[p]deletechar` to start over.")
                return

            # Create the character
            character = {
                "name": name,
                "race": race.capitalize(),
                "gender": gender.capitalize(),
                "backstory": backstory,
                "level": 1,
                "health": 100,
                "strength": 10,
                "experience": 0,
            }

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

    @commands.command()
    async def charinfo(self, ctx):
        """View your character's information."""
        character = await self.config.user(ctx.author).character()
        if not character:
            await ctx.send("You don't have a character yet! Use `[p]createchar` to create one.")
            return

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

