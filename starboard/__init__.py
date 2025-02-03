from .starboard import Starboard

async def setup(bot):
    await bot.add_cog(Starboard(bot))