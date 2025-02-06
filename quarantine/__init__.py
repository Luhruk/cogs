from .quarantine import Quarantine

async def setup(bot):
    await bot.add_cog(Quarantine(bot))
