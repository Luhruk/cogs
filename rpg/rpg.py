from redbot.core import commands
from . import character

class RPG(commands.Cog):
    """Main RPG commands group."""

    def __init__(self, bot):
        self.bot = bot
        self.character_commands = character.CharacterCommands(bot)

    @commands.group(invoke_without_command=True)
    async def rpg(self, ctx):
        """Main RPG commands group."""
        await ctx.send_help(ctx.command)

    @rpg.group(invoke_without_command=True)
    async def char(self, ctx):
        """Character-related commands."""
        await ctx.send_help(ctx.command)

    @char.command()
    async def create(self, ctx):
        """Create a new character."""
        await self.character_commands.create(ctx)

    @char.command()
    async def info(self, ctx):
        """View your character's information."""
        await self.character_commands.info(ctx)

    @char.command()
    async def list(self, ctx):
        """List all of your characters."""
        await self.character_commands.list(ctx)

    @char.command()
    async def delete(self, ctx, character_name: str):
        """Delete a specific character."""
        await self.character_commands.delete(ctx, character_name)
