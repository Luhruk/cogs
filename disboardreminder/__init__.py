from redbot.core.utils import get_end_user_data_statement

from .core import DisboardReminder

__red_end_user_data_statement__ = get_end_user_data_statement(__file__)


async def setup(bot):
    cog = DisboardReminder(bot)
    await bot.add_cog(cog)