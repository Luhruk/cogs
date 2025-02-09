from redbot.core import commands, Config
from redbot.core.bot import Red
from typing import Optional
from discord.utils import get


class SyndicatePoints(commands.Cog):
    """A cog to manage syndicates and track points assigned by moderators."""
    
    def __init__(self, bot: Red):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=1234567890)
        self.config.register_guild(syndicates={}, mod_role=None)
    
    @commands.admin()
    @commands.guild_only()
    @commands.command()
    async def setmodrole(self, ctx, *, role_name: str):
        """Set the moderator role for this cog."""
        role = get(ctx.guild.roles, name=role_name)
        if not role:
            await ctx.send(f"Role `{role_name}` not found. Make sure you typed it exactly as it appears in Discord.")
            return
        await self.config.guild(ctx.guild).mod_role.set(role.id)
        await ctx.send(f"Moderator role set to `{role_name}`.")
    
    def is_moderator():
        async def predicate(ctx):
            mod_role_id = await ctx.cog.config.guild(ctx.guild).mod_role()
            if mod_role_id and any(r.id == mod_role_id for r in ctx.author.roles):
                return True
            return False
        return commands.check(predicate)
    
    @is_moderator()
    @commands.guild_only()
    @commands.command()
    async def createsyndicate(self, ctx, syndicate_name: str):
        """Create a new syndicate."""
        async with self.config.guild(ctx.guild).syndicates() as syndicates:
            if syndicate_name in syndicates:
                await ctx.send(f"Syndicate `{syndicate_name}` already exists.")
                return
            syndicates[syndicate_name] = 0
        await ctx.send(f"Syndicate `{syndicate_name}` has been created.")
    
    @is_moderator()
    @commands.guild_only()
    @commands.command()
    async def deletesyndicate(self, ctx, syndicate_name: str):
        """Delete an existing syndicate."""
        async with self.config.guild(ctx.guild).syndicates() as syndicates:
            if syndicate_name not in syndicates:
                await ctx.send(f"Syndicate `{syndicate_name}` does not exist.")
                return
            del syndicates[syndicate_name]
        await ctx.send(f"Syndicate `{syndicate_name}` has been deleted.")
    
    @is_moderator()
    @commands.guild_only()
    @commands.command()
    async def addpoints(self, ctx, syndicate_name: str, points: int):
        """Add points to a syndicate."""
        async with self.config.guild(ctx.guild).syndicates() as syndicates:
            if syndicate_name not in syndicates:
                await ctx.send(f"Syndicate `{syndicate_name}` does not exist.")
                return
            syndicates[syndicate_name] += points
        await ctx.send(f"Added {points} points to `{syndicate_name}`. Total: {syndicates[syndicate_name]}")
    
    @is_moderator()
    @commands.guild_only()
    @commands.command()
    async def removepoints(self, ctx, syndicate_name: str, points: int):
        """Remove points from a syndicate."""
        async with self.config.guild(ctx.guild).syndicates() as syndicates:
            if syndicate_name not in syndicates:
                await ctx.send(f"Syndicate `{syndicate_name}` does not exist.")
                return
            syndicates[syndicate_name] -= points
        await ctx.send(f"Removed {points} points from `{syndicate_name}`. Total: {syndicates[syndicate_name]}")
    
    @is_moderator()
    @commands.guild_only()
    @commands.command()
    async def resetpoints(self, ctx):
        """Reset all syndicate points to 0."""
        async with self.config.guild(ctx.guild).syndicates() as syndicates:
            for syndicate in syndicates:
                syndicates[syndicate] = 0
        await ctx.send("All syndicate points have been reset to 0.")
    
    @commands.guild_only()
    @commands.command()
    async def syndicatepoints(self, ctx, syndicate_name: Optional[str] = None):
        """Check points of a syndicate or all syndicates."""
        syndicates = await self.config.guild(ctx.guild).syndicates()
        if syndicate_name:
            if syndicate_name not in syndicates:
                await ctx.send(f"Syndicate `{syndicate_name}` does not exist.")
                return
            await ctx.send(f"`{syndicate_name}` has {syndicates[syndicate_name]} points.")
        else:
            if not syndicates:
                await ctx.send("No syndicates available.")
                return
            leaderboard = "\n".join(f"{name}: {points} points" for name, points in sorted(syndicates.items(), key=lambda x: x[1], reverse=True))
            await ctx.send(f"**Syndicate Leaderboard:**\n{leaderboard}")

async def setup(bot: Red):
    await bot.add_cog(SyndicatePoints(bot))
