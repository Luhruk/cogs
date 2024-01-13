from .nominatepresident import PresidentCog


async def setup(bot):
    await bot.add_cog(PresidentCog(bot))