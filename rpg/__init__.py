from redbot.core import commands  # Import Red's commands framework
from .character import Character  # Import Character class from character.py
from .inventory import Inventory  # Import Inventory class from inventory.py
from .combat import Combat  # Import Combat class from combat.py
from .quests import Quests  # Import Quests class from quests.py
from .world import World  # Import World class from world.py
from .spells import Spells  # Import Spells class from spells.py
from .data_handler import DataHandler  # Import DataHandler class from data_handler.py

class RPGCog(commands.Cog):  # Ensure this inherits from commands.Cog
    """A fully functional RPG cog for Red Discord Bot."""

    def __init__(self, bot):
        self.bot = bot
        print("Initializing RPGCog...")

        # Initialize all components
        self.data_handler = DataHandler("data/")  # Initialize DataHandler with the data folder
        self.character = Character(self.data_handler)  # Initialize Character
        self.inventory = Inventory(self.data_handler)  # Initialize Inventory
        self.combat = Combat(self.data_handler)  # Initialize Combat
        self.quests = Quests(self.data_handler)  # Initialize Quests
        self.world = World(self.data_handler)  # Initialize World
        self.spells = Spells(self.data_handler)  # Initialize Spells

        print("RPGCog initialized successfully!")

    @commands.command()
    async def test_rpg(self, ctx):
        """Test command to check if the cog is working."""
        await ctx.send("RPGCog is loaded and working!")

# Required setup function for Red
async def setup(bot):
    """Adds the RPGCog to the bot."""
    await bot.add_cog(RPGCog(bot))  # Properly add the cog
