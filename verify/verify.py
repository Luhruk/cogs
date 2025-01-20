# verify.py
from redbot.core import commands, Config
from discord import Member, Role

class Verify(commands.Cog):
    """Verification Cog for Red Discord Bot."""

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=1234567890)
        default_guild = {
            "verified_role": None,
            "punishment_role": None,
            "trigger_role": None
        }
        self.config.register_guild(**default_guild)

    @commands.guild_only()
    @commands.admin_or_permissions(manage_roles=True)
    @commands.command()
    async def setverifiedrole(self, ctx, role: Role):
        """Set the role to be assigned upon verification."""
        await self.config.guild(ctx.guild).verified_role.set(role.id)
        await ctx.send(f"Verified role set to: {role.name}")

    @commands.guild_only()
    @commands.admin_or_permissions(manage_roles=True)
    @commands.command()
    async def setpunishmentrole(self, ctx, role: Role):
        """Set the punishment role for unverified users."""
        await self.config.guild(ctx.guild).punishment_role.set(role.id)
        await ctx.send(f"Punishment role set to: {role.name}")

    @commands.guild_only()
    @commands.admin_or_permissions(manage_roles=True)
    @commands.command()
    async def settriggerrole(self, ctx, role: Role):
        """Set the role that triggers verification check."""
        await self.config.guild(ctx.guild).trigger_role.set(role.id)
        await ctx.send(f"Trigger role set to: {role.name}")

    @commands.Cog.listener()
    async def on_member_update(self, before: Member, after: Member):
        if before.guild != after.guild:
            return

        guild_config = await self.config.guild(after.guild).all()
        trigger_role_id = guild_config["trigger_role"]
        verified_role_id = guild_config["verified_role"]
        punishment_role_id = guild_config["punishment_role"]

        if not (trigger_role_id and verified_role_id and punishment_role_id):
            return

        trigger_role = after.guild.get_role(trigger_role_id)
        verified_role = after.guild.get_role(verified_role_id)
        punishment_role = after.guild.get_role(punishment_role_id)

        if trigger_role in after.roles and verified_role not in after.roles:
            if punishment_role not in after.roles:
                await after.add_roles(punishment_role, reason="User lacks verification.")

    @commands.guild_only()
    @commands.command()
    async def verify(self, ctx, member: Member):
        """Manually verify a user."""
        verified_role_id = await self.config.guild(ctx.guild).verified_role()
        if not verified_role_id:
            await ctx.send("Verified role is not set.")
            return

        verified_role = ctx.guild.get_role(verified_role_id)
        if not verified_role:
            await ctx.send("Verified role no longer exists.")
            return

        await member.add_roles(verified_role, reason="Manually verified by admin.")
        await ctx.send(f"{member.display_name} has been verified.")
