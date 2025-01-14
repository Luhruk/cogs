from discord.ext import commands
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
        self.data_handler = DataHandler("data/")
        self.character = Character(self.data_handler)
        self.inventory = Inventory(self.data_handler)
        self.combat = Combat(self.data_handler)
        self.quests = Quests(self.data_handler)
        self.world = World(self.data_handler)
        self.spells = Spells(self.data_handler)
        print("RPGCog initialized successfully!")


async def setup(bot):
    """Adds the RPGCog to the bot."""
    print("Setting up RPGCog...")
    await bot.add_cog(RPGCog(bot))
    print("RPGCog successfully loaded!")
