from redbot.core import commands

class RPG(commands.Cog):
    """A role-playing game cog"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def rpgstart(self, ctx):
        """Start your RPG adventure!"""
        await ctx.send(f"Welcome to the RPG adventure, {ctx.author.mention}!")
