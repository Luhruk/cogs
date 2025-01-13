from redbot.core import commands, Config
import discord
import asyncio


class CharacterCommands(commands.Cog):
    """Character-related commands for the RPG cog."""

    def __init__(self, bot, config):
        self.bot = bot
        self.config = config

    @commands.group(name="char", invoke_without_command=True)
    async def char(self, ctx):
        """Character-related commands."""
        await ctx.send_help(ctx.command)

    @char.command()
    async def create(self, ctx):
        """Interactive character creation."""
        character = {}
        prompts = [
            ("What would you like your character's name to be?", "name"),
            ("What is your character's race (e.g., Human, Elf, Orc)?", "race"),
            ("What is your character's gender?", "gender"),
            ("What is your character's backstory? (Optional)", "backstory"),
            ("Provide a URL for your character's image. (Optional)", "image_url"),
        ]

        for prompt, field in prompts:
            await ctx.send(prompt)
            try:
                message = await self.bot.wait_for(
                    "message", timeout=60, check=lambda m: m.author == ctx.author and m.channel == ctx.channel
                )
                character[field] = message.content
            except asyncio.TimeoutError:
                await ctx.send("You took too long to respond. Character creation canceled.")
                return

        character["level"] = 1
        character["health"] = 100
        character["strength"] = 10
        character["experience"] = 0

        user_data = await self.config.user(ctx.author).characters()
        user_data.append(character)
        await self.config.user(ctx.author).characters.set(user_data)

        await ctx.send(f"Character **{character['name']}** created successfully!")

    @char.command()
    async def info(self, ctx):
        """View your active character's information."""
        user_data = await self.config.user(ctx.author).all()
        active_index = user_data.get("active_character")

        if active_index is None:
            await ctx.send("You have no active character. Use `.char setactive` to choose one.")
            return

        try:
            character = user_data["characters"][active_index]
        except IndexError:
            await ctx.send("Your active character index is invalid. Please reset it with `.char setactive`.")
            return

        embed = discord.Embed(title=f"{ctx.author.display_name}'s Character", color=discord.Color.green())
        embed.add_field(name="Name", value=character["name"], inline=False)
        embed.add_field(name="Race", value=character["race"], inline=False)
        embed.add_field(name="Gender", value=character["gender"], inline=False)
        embed.add_field(name="Backstory", value=character.get("backstory", "None"), inline=False)
        embed.add_field(name="Level", value=character["level"], inline=True)
        embed.add_field(name="Health", value=character["health"], inline=True)
        embed.add_field(name="Strength", value=character["strength"], inline=True)
        embed.add_field(name="Experience", value=character["experience"], inline=True)

        if character.get("image_url"):
            embed.set_thumbnail(url=character["image_url"])

        await ctx.send(embed=embed)

    @char.command()
    async def list(self, ctx):
        """List all your characters."""
        user_data = await self.config.user(ctx.author).characters()

        if not user_data:
            await ctx.send("You have no characters. Use `.char create` to create one.")
            return

        embed = discord.Embed(title=f"{ctx.author.display_name}'s Characters", color=discord.Color.blue())
        for i, character in enumerate(user_data):
            embed.add_field(
                name=f"Character {i + 1}",
                value=f"**Name**: {character['name']}\n**Level**: {character['level']}",
                inline=False,
            )

        await ctx.send(embed=embed)

    @char.command()
    async def setactive(self, ctx, index: int):
        """Set your active character by choosing its index."""
        user_data = await self.config.user(ctx.author).characters()

        if index < 1 or index > len(user_data):
            await ctx.send("Invalid character index.")
            return

        await self.config.user(ctx.author).active_character.set(index - 1)
        await ctx.send(f"Character {index} is now your active character.")

    @char.command()
    async def delete(self, ctx, index: int):
        """Delete a specific character by index."""
        user_data = await self.config.user(ctx.author).characters()

        if index < 1 or index > len(user_data):
            await ctx.send("Invalid character index.")
            return

        deleted_character = user_data.pop(index - 1)
        await self.config.user(ctx.author).characters.set(user_data)

        if await self.config.user(ctx.author).active_character() == index - 1:
            await self.config.user(ctx.author).active_character.set(None)

        await ctx.send(f"Character **{deleted_character['name']}** has been deleted.")
