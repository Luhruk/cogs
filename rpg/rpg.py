from redbot.core import commands
from .character import Character

class RPG(commands.Cog):
    """Main RPG cog"""

    def __init__(self, bot):
        self.bot = bot
        self.character_commands = Character(bot)

    @commands.group()
    async def rpg(self, ctx):
        """Main RPG command group."""
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @rpg.group()
    async def char(self, ctx):
        """Character-related commands."""
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @rpg.command()
    async def help(self, ctx):
        """Show help for RPG commands."""
        await ctx.send_help(ctx.command)

    # Other RPG-related commands can be added here as needed
