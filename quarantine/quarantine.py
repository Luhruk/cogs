from redbot.core import commands
import discord

class Quarantine(commands.Cog):
    """Cog to manage a quarantine role."""

    def __init__(self, bot):
        self.bot = bot
        self.quarantine_role_id = None  # Store the role ID

    @commands.admin()
    @commands.command()
    async def setquarantine(self, ctx, role: discord.Role):
        """Set the quarantine role."""
        self.quarantine_role_id = role.id
        await ctx.send(f"Quarantine role set to: {role.name}")

    @commands.admin()
    @commands.command()
    async def quarantine(self, ctx, member: discord.Member):
        """Assign the quarantine role to a user."""
        if self.quarantine_role_id is None:
            await ctx.send("Quarantine role not set. Use `setquarantine` first.")
            return
        role = ctx.guild.get_role(self.quarantine_role_id)
        if role is None:
            await ctx.send("Invalid quarantine role.")
            return
        await member.add_roles(role)
        await ctx.send(f"{member.display_name} has been quarantined.")

    @commands.admin()
    @commands.command()
    async def unquarantine(self, ctx, member: discord.Member):
        """Remove the quarantine role from a user."""
        if self.quarantine_role_id is None:
            await ctx.send("Quarantine role not set. Use `setquarantine` first.")
            return
        role = ctx.guild.get_role(self.quarantine_role_id)
        if role is None:
            await ctx.send("Invalid quarantine role.")
            return
        await member.remove_roles(role)
        await ctx.send(f"{member.display_name} has been unquarantined.")

async def setup(bot):
    await bot.add_cog(Quarantine(bot))
