from .modmail import ModMail  # Correct the case to match the class name

async def setup(bot):
    await bot.add_cog(ModMail(bot))  # Use ModMail with the correct case
