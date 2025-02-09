from redbot.core import commands, Config
from redbot.core.bot import Red
import discord
from typing import Optional

class SyndicatePoints(commands.Cog):
    """A cog to manage syndicates and track points assigned by moderators."""
    
    def __init__(self, bot: Red):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=1234567890)
        self.config.register_guild(syndicates={}, mod_role=None, leaderboard_message=None)
    
    @commands.admin()
    @commands.guild_only()
    @commands.command()
    async def setmodrole(self, ctx, *, role_name: str):
        """Set the moderator role for this cog."""
        role = discord.utils.get(ctx.guild.roles, name=role_name)
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
        await self.update_leaderboard(ctx)
    
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
        await self.update_leaderboard(ctx)
    
    @is_moderator()
    @commands.guild_only()
    @commands.command()
    async def resetpoints(self, ctx):
        """Reset all syndicate points to 0."""
        async with self.config.guild(ctx.guild).syndicates() as syndicates:
            for syndicate in syndicates:
                syndicates[syndicate] = 0
        await self.update_leaderboard(ctx)
    
    async def update_leaderboard(self, ctx):
        """Update the embedded leaderboard message."""
        syndicates = await self.config.guild(ctx.guild).syndicates()
        if not syndicates:
            return
        sorted_syndicates = sorted(syndicates.items(), key=lambda x: x[1], reverse=True)
        embed = discord.Embed(title="Syndicate Leaderboard", color=discord.Color.blue())
        for name, points in sorted_syndicates:
            embed.add_field(name=name, value=f"{points} points", inline=False)
        
        leaderboard_message_id = await self.config.guild(ctx.guild).leaderboard_message()
        if leaderboard_message_id:
            try:
                message = await ctx.channel.fetch_message(leaderboard_message_id)
                await message.edit(embed=embed)
            except discord.NotFound:
                leaderboard_message_id = None
        
        if not leaderboard_message_id:
            message = await ctx.send(embed=embed)
            await self.config.guild(ctx.guild).leaderboard_message.set(message.id)
    
    @commands.guild_only()
    @commands.command()
    async def syndicateleaderboard(self, ctx):
        """Post or update the syndicate leaderboard."""
        await self.update_leaderboard(ctx)
        await ctx.send("Leaderboard updated!")

async def setup(bot: Red):
    await bot.add_cog(SyndicatePoints(bot))
