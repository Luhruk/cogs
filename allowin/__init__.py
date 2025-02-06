from .allowin import AllowIn

async def setup(bot):
    await bot.add_cog(AllowIn(bot))
