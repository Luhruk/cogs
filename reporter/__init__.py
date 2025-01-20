from .reporter import Reporter

async def setup(bot):
    await bot.add_cog(Reporter(bot))
