import discord
from redbot.core import commands, Config
import asyncio
from datetime import datetime, timedelta

class RoleReminder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=123456789)
        self.config.register_guild(role=None, channel=None, tracked_users={}, reminder_delay=3, ping_role=None)
        self.check_reminders.start()

    def cog_unload(self):
        self.check_reminders.cancel()

    @commands.guild_only()
    @commands.admin_or_permissions(manage_roles=True)
    @commands.command()
    async def setreminderrole(self, ctx, role: discord.Role):
        """Set the role to track for reminders."""
        await self.config.guild(ctx.guild).role.set(role.id)
        await ctx.send(f"Tracking reminders for role: {role.name}")

    @commands.guild_only()
    @commands.admin_or_permissions(manage_channels=True)
    @commands.command()
    async def setreminderchannel(self, ctx, channel: discord.TextChannel):
        """Set the channel where reminders will be sent."""
        await self.config.guild(ctx.guild).channel.set(channel.id)
        await ctx.send(f"Reminders will be sent in: {channel.mention}")

    @commands.guild_only()
    @commands.admin_or_permissions(manage_roles=True)
    @commands.command()
    async def setpingrole(self, ctx, role: discord.Role):
        """Set the role to be pinged in reminders."""
        await self.config.guild(ctx.guild).ping_role.set(role.id)
        await ctx.send(f"Reminders will also ping: {role.mention}")

    @commands.guild_only()
    @commands.admin_or_permissions(manage_guild=True)
    @commands.command()
    async def setreminderdelay(self, ctx, days: int):
        """Set the delay (in days) before the reminder is sent."""
        if days < 1:
            await ctx.send("The reminder delay must be at least 1 day.")
            return
        await self.config.guild(ctx.guild).reminder_delay.set(days)
        await ctx.send(f"Reminder delay set to {days} days.")

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        guild = after.guild
        role_id = await self.config.guild(guild).role()
        if not role_id:
            return
        role = guild.get_role(role_id)
        if not role:
            return

        if role in after.roles and role not in before.roles:
            reminder_delay = await self.config.guild(guild).reminder_delay()
            tracked_users = await self.config.guild(guild).tracked_users()
            tracked_users[str(after.id)] = (datetime.utcnow() + timedelta(days=reminder_delay)).timestamp()
            await self.config.guild(guild).tracked_users.set(tracked_users)

    @tasks.loop(minutes=30)
    async def check_reminders(self):
        for guild in self.bot.guilds:
            role_id = await self.config.guild(guild).role()
            channel_id = await self.config.guild(guild).channel()
            ping_role_id = await self.config.guild(guild).ping_role()
            tracked_users = await self.config.guild(guild).tracked_users()
            if not role_id or not channel_id or not tracked_users:
                continue

            channel = guild.get_channel(channel_id)
            if not channel:
                continue

            ping_role = guild.get_role(ping_role_id) if ping_role_id else None
            ping_text = f" {ping_role.mention}" if ping_role else ""

            now = datetime.utcnow().timestamp()
            to_remove = []
            for user_id, timestamp in tracked_users.items():
                if now >= timestamp:
                    member = guild.get_member(int(user_id))
                    if member:
                        await channel.send(f"{member.mention} was restricted {await self.config.guild(guild).reminder_delay()} days ago, please review.{ping_text}")
                    to_remove.append(user_id)

            for user_id in to_remove:
                del tracked_users[user_id]
            await self.config.guild(guild).tracked_users.set(tracked_users)

    @check_reminders.before_loop
    async def before_check_reminders(self):
        await self.bot.wait_until_red_ready()

async def setup(bot):
    cog = RoleReminder(bot)
    bot.add_cog(cog)
