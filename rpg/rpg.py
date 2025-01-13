from redbot.core import commands
from .character import CharacterCommands

class RPG(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.character_commands = CharacterCommands(bot)

    @commands.group()
    async def rpg(self, ctx):
        """Main RPG command group."""
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @rpg.command()
    async def char(self, ctx):
        """Character-related commands."""
        await ctx.send_help(ctx.command)

    @rpg.command()
    async def info(self, ctx):
        """Get your character info."""
        await self.character_commands.info(ctx)

    @rpg.command()
    async def list(self, ctx):
        """List your characters."""
        await self.character_commands.list(ctx)

    @rpg.command()
    async def setactive(self, ctx, character_name: str):
        """Set a character as active."""
        await self.character_commands.setactive(ctx, character_name)
