from discord.ext import commands

# Import other modules here
from .character import Character
from .inventory import Inventory
from .combat import Combat
from .quests import Quests
from .world import World
from .spells import Spells
from .data_handler import DataHandler


class RPGCog(commands.Cog):
    """A fully functional RPG cog for Red Discord Bot."""

    def __init__(self, bot):
        self.bot = bot
        print("Initializing RPGCog...")

        # Initialize components
        self.data_handler = DataHandler("data/")
        self.character = Character(self.data_handler)
        self.inventory = Inventory(self.data_handler)
        self.combat = Combat(self.data_handler)
        self.quests = Quests(self.data_handler)
        self.world = World(self.data_handler)
        self.spells = Spells(self.data_handler)

        print("RPGCog initialized successfully!")

    @commands.command()
    async def test_rpg(self, ctx):
        """Test command to check if the cog is working."""
        await ctx.send("RPGCog is loaded and working!")


# Required setup function for Red
async def setup(bot):
    """Adds the RPGCog to the bot."""
    await bot.add_cog(RPGCog(bot))
