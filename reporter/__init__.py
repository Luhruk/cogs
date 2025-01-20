import logging

log = logging.getLogger(__name__)

async def setup(bot):
    try:
        log.info("Attempting to add Reporter cog...")
        # The cog is already added in reporter.py, so no need to add it here again
        log.info("Reporter cog added successfully.")
    except Exception as e:
        log.error(f"Error loading Reporter cog: {e}")
        raise
