from discord.ext import commands
from .character import Character
from .inventory import Inventory
from .combat import Combat
from .quests import Quests
from .world import World
from .spells import Spells
from .data_handler import DataHandler

class RPGCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data_handler = DataHandler("data/")
        self.character = Character(self.data_handler)
        self.inventory = Inventory(self.data_handler)
        self.combat = Combat(self.data_handler)
        self.quests = Quests(self.data_handler)
        self.world = World(self.data_handler)
        self.spells = Spells(self.data_handler)

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} loaded!")

def setup(bot):
    bot.add_cog(RPGCog(bot))
