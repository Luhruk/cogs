from .rolereminder import RoleReminder

async def setup(bot):
    cog = RoleReminder(bot)
    await bot.add_cog(cog)
