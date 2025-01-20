import logging
from .reporter import Reporter

log = logging.getLogger(__name__)

async def setup(bot):
    try:
        log.info("Attempting to add Reporter cog...")
        await bot.add_cog(Reporter(bot))
        log.info("Reporter cog added successfully.")
    except Exception as e:
        log.error(f"Error loading Reporter cog: {e}")
