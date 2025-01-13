from redbot.core import commands, Config
from .character import CharacterCommands


class RPG(commands.Cog):
    """Main RPG cog."""

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=1234567890, force_registration=True)
        default_user = {
            "characters": [],  # List of characters
            "active_character": None,  # Index of active character
        }
        self.config.register_user(**default_user)

        # Initialize character commands
        self.character_commands = CharacterCommands(bot, self.config)

    @commands.group(invoke_without_command=True)
    async def rpg(self, ctx):
        """Main RPG command group."""
        await ctx.send_help(ctx.command)

    @rpg.group(name="char", invoke_without_command=True)
    async def char(self, ctx):
        """Character-related commands."""
        await ctx.send_help(ctx.command)

    @char.command()
    async def create(self, ctx):
        """Interactive character creation."""
        await self.character_commands.create(ctx)

    @char.command()
    async def info(self, ctx):
        """View your active character's information."""
        await self.character_commands.info(ctx)

    @char.command()
    async def list(self, ctx):
        """List all your characters."""
        await self.character_commands.list(ctx)

    @char.command()
    async def setactive(self, ctx, index: int):
        """Set your active character by choosing its index."""
        await self.character_commands.setactive(ctx, index)

    @char.command()
    async def delete(self, ctx, index: int):
        """Delete a specific character by index."""
        await self.character_commands.delete(ctx)
