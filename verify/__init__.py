# __init__.py
from .verify import Verify

async def setup(bot):
    await bot.add_cog(Verify(bot))
