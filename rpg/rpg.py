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
        self.rpg_group = commands.Group(name="char", invoke_without_command=True)
        self.character_commands.register_to(self.rpg_group)

    @commands.group(invoke_without_command=True)
    async def rpg(self, ctx):
        """Main RPG command group."""
        await ctx.send_help(ctx.command)

    @rpg.command()
    async def char(self, ctx):
        """Character-related commands."""
        await ctx.send_help(self.character_commands)
