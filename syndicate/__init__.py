from redbot.core.bot import Red
from .syndicate import SyndicatePoints

async def setup(bot: Red):
    await bot.add_cog(SyndicatePoints(bot))
