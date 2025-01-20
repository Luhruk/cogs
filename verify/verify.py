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
            "trigger_role": None,
            "verified_users": {},  # Dictionary to store verified user IDs
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

    @commands.guild_only()
    @commands.admin_or_permissions(manage_roles=True)
    @commands.command()
    async def status(self, ctx):
        """Show the status of the guild's verification settings."""
        guild_config = await self.config.guild(ctx.guild).all()
        trigger_role = ctx.guild.get_role(guild_config["trigger_role"]) if guild_config["trigger_role"] else None
        verified_role = ctx.guild.get_role(guild_config["verified_role"]) if guild_config["verified_role"] else None
        punishment_role = ctx.guild.get_role(guild_config["punishment_role"]) if guild_config["punishment_role"] else None
        await ctx.send(
            f"Trigger Role: {trigger_role.name if trigger_role else 'Not set'}\n"
            f"Verified Role: {verified_role.name if verified_role else 'Not set'}\n"
            f"Punishment Role: {punishment_role.name if punishment_role else 'Not set'}"
        )

    @commands.Cog.listener()
    async def on_member_join(self, member: Member):
        """Handle member join and assign trigger role to alt accounts."""
        trigger_role_id = await self.config.guild(member.guild).trigger_role()
        verified_role_id = await self.config.guild(member.guild).verified_role()
        punishment_role_id = await self.config.guild(member.guild).punishment_role()

        # Check if the user has been verified before
        verified_user_id = await self.config.guild(member.guild).verified_user(member.id)

        # If the user is verified, don't apply the punishment or trigger roles
        if verified_user_id:
            return  # User is verified, no need to assign punishment or trigger role

        # If the user is not verified, assign the trigger role
        trigger_role = member.guild.get_role(trigger_role_id)
        if trigger_role:
            await member.add_roles(trigger_role, reason="User is unverified.")

        # Assign punishment role if the user lacks verification
        punishment_role = member.guild.get_role(punishment_role_id)
        if punishment_role:
            await member.add_roles(punishment_role, reason="User lacks verification.")

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
        
        # Store the user as verified in the database
        await self.config.guild(ctx.guild).verified_user.set(member.id)
        
        await ctx.send(f"{member.display_name} has been verified.")
    
    async def is_verified(self, guild, user_id: int):
        """Check if a user is verified in the database."""
        return await self.config.guild(guild).verified_user(user_id) is not None

    async def set_verified(self, guild, user_id: int):
        """Set a user as verified in the database."""
        await self.config.guild(guild).verified_user.set(user_id)
