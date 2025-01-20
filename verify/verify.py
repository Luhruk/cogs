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

    async def add_verified_user(self, user_id: int, username: str):
        """Add a user to the verified users database."""
        await self.db.execute("INSERT INTO verified_users (user_id, username) VALUES (?, ?)", (user_id, username))
        await self.db.commit()

    async def remove_verified_user(self, user_id: int):
        """Remove a user from the verified users database."""
        await self.db.execute("DELETE FROM verified_users WHERE user_id = ?", (user_id,))
        await self.db.commit()

    async def is_verified(self, user_id: int) -> bool:
        """Check if a user is verified."""
        async with self.db.execute("SELECT 1 FROM verified_users WHERE user_id = ?", (user_id,)) as cursor:
            result = await cursor.fetchone()
            return result is not None

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
    async def on_member_join(self, member: Member):
        """Handle member join and assign trigger role to alt accounts."""
        trigger_role_id = await self.config.guild(member.guild).trigger_role()
        verified_role_id = await self.config.guild(member.guild).verified_role()
        punishment_role_id = await self.config.guild(member.guild).punishment_role()

        if await self.is_verified(member.id):
            return  # Verified users can join without issue

        # Assign trigger role to alt accounts
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
        verified_role = ctx.guild.get_role(verified_role_id)
        if not verified_role:
            await ctx.send("Verified role no longer exists.")
            return

        # Add the verified role to the user
        await member.add_roles(verified_role, reason="Manually verified by admin.")

        # Add the user to the database
        await self.add_verified_user(member.id, member.name)

        await ctx.send(f"{member.display_name} has been verified.")

    @commands.guild_only()
    @commands.command()
    async def unlink(self, ctx, member: Member):
        """Remove a user's verified status."""
        await self.remove_verified_user(member.id)
        await ctx.send(f"{member.display_name} has been unverified.")

    @commands.guild_only()
    @commands.command()
    async def status(self, ctx):
        """Show the current configuration status for the verification system."""
        # Retrieve the settings from the configuration
        guild_config = await self.config.guild(ctx.guild).all()
        
        verified_role_id = guild_config["verified_role"]
        punishment_role_id = guild_config["punishment_role"]
        trigger_role_id = guild_config["trigger_role"]

        # Get the roles from the guild
        verified_role = ctx.guild.get_role(verified_role_id) if verified_role_id else None
        punishment_role = ctx.guild.get_role(punishment_role_id) if punishment_role_id else None
        trigger_role = ctx.guild.get_role(trigger_role_id) if trigger_role_id else None

        # Build the status message
        status_message = "Verification System Status:\n"
        status_message += f"**Verified Role**: {verified_role.name if verified_role else 'Not set'}\n"
        status_message += f"**Punishment Role**: {punishment_role.name if punishment_role else 'Not set'}\n"
        status_message += f"**Trigger Role**: {trigger_role.name if trigger_role else 'Not set'}\n"

        await ctx.send(status_message)
