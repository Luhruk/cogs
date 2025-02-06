from redbot.core import commands
import discord

class AllowIn(commands.Cog):
    """Cog to manage role removal for allowing users in."""

    def __init__(self, bot):
        self.bot = bot
        self.restricted_role_id = None  # Store the restricted role ID

    @commands.admin()
    @commands.command()
    async def setrestricted(self, ctx, role: discord.Role):
        """Set the restricted role to be removed by allowin."""
        self.restricted_role_id = role.id
        await ctx.send(f"Restricted role set to: {role.name}")

    @commands.admin()
    @commands.command()
    async def allowin(self, ctx, member: discord.Member):
        """Remove the restricted role from a user."""
        if self.restricted_role_id is None:
            await ctx.send("Restricted role not set. Use `setrestricted` first.")
            return
        role = ctx.guild.get_role(self.restricted_role_id)
        if role is None:
            await ctx.send("Invalid restricted role.")
            return
        await member.remove_roles(role)
        await ctx.send(f"{member.display_name} has been allowed in.")

async def setup(bot):
    await bot.add_cog(AllowIn(bot))