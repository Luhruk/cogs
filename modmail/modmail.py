from redbot.core import commands, Config
import discord
from discord.utils import get

class Modmail(commands.Cog):
    """Modmail system for handling muted users."""

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=1234567890, force_registration=True)
        default_guild = {
            "muted_role": None,
            "modmail_channel": None,
            "log_channel": None
        }
        self.config.register_guild(**default_guild)

    @commands.guild_only()
    @commands.admin_or_permissions(manage_guild=True)
    @commands.group()
    async def modmailset(self, ctx):
        """Configuration commands for modmail."""
        pass

    @modmailset.command()
    async def mutedrole(self, ctx, role: discord.Role):
        """Set the role that triggers a modmail thread."""
        await self.config.guild(ctx.guild).muted_role.set(role.id)
        await ctx.send(f"Muted role set to {role.name}.")

    @modmailset.command()
    async def modmailchannel(self, ctx, channel: discord.TextChannel):
        """Set the channel where modmail threads will be created."""
        await self.config.guild(ctx.guild).modmail_channel.set(channel.id)
        await ctx.send(f"Modmail channel set to {channel.mention}.")

    @modmailset.command()
    async def logchannel(self, ctx, channel: discord.TextChannel):
        """Set the channel where modmail logs will be sent."""
        await self.config.guild(ctx.guild).log_channel.set(channel.id)
        await ctx.send(f"Log channel set to {channel.mention}.")

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        guild = after.guild
        muted_role_id = await self.config.guild(guild).muted_role()
        modmail_channel_id = await self.config.guild(guild).modmail_channel()

        if not muted_role_id or not modmail_channel_id:
            return

        muted_role = get(guild.roles, id=muted_role_id)
        modmail_channel = guild.get_channel(modmail_channel_id)

        if not muted_role or not modmail_channel:
            return

        # Check if the muted role was added
        if muted_role not in before.roles and muted_role in after.roles:
            thread_name = f"modmail-{after.name}"
            thread = await modmail_channel.create_thread(name=thread_name, type=discord.ChannelType.public_thread)
            await thread.add_user(after)
            await thread.send(
                f"Hello {after.mention}, this is your appeal ticket. Please explain your situation here, and a moderator will respond shortly."
            )

            # Log the creation
            log_channel_id = await self.config.guild(guild).log_channel()
            if log_channel_id:
                log_channel = guild.get_channel(log_channel_id)
                if log_channel:
                    await log_channel.send(
                        f"A modmail thread has been created for {after.mention} in {thread.mention}."
                    )

    @commands.guild_only()
    @commands.admin_or_permissions(manage_guild=True)
    @commands.command()
    async def closemodmail(self, ctx, thread: discord.Thread):
        """Close a modmail thread."""
        if thread.owner != ctx.guild.me:
            await ctx.send("I can only close threads created by me.")
            return

        await thread.edit(archived=True, locked=True)
        await ctx.send(f"Thread {thread.name} has been closed.")

        # Log the closure
        log_channel_id = await self.config.guild(ctx.guild).log_channel()
        if log_channel_id:
            log_channel = ctx.guild.get_channel(log_channel_id)
            if log_channel:
                await log_channel.send(f"Thread {thread.name} was closed by {ctx.author.mention}.")

async def setup(bot):
    await bot.add_cog(Modmail(bot))
