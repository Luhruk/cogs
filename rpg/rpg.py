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

        # Add character-related commands
        self.bot.add_cog(CharacterCommands(bot, self.config))

    @commands.group(invoke_without_command=True)
    async def rpg(self, ctx):
        """Main RPG command group."""
        await ctx.send_help(ctx.command)
