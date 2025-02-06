from redbot.core import commands, Config
import discord
from discord.utils import get
import io
from discord import AllowedMentions

class Modmail(commands.Cog):
    """Modmail system for handling muted users."""

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=1234567890, force_registration=True)
        default_guild = {
            "muted_role": None,
            "modmail_channel": None,
            "log_channel": None,
            "moderator_roles": [],  # Change this to a list for multiple roles
            "thread_history": {}
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

    @modmailset.command()
    async def moderatorrole(self, ctx, *roles: discord.Role):
        """Add one or more roles to be pinged in modmail threads."""
        role_ids = [role.id for role in roles]
        await self.config.guild(ctx.guild).moderator_roles.set(role_ids)
        role_names = [role.name for role in roles]
        await ctx.send(f"Moderator roles set to: {', '.join(role_names)}.")

    @commands.guild_only()
    @commands.admin_or_permissions(manage_guild=True)
    @commands.command()
    async def modmailstatus(self, ctx):
        """Show the current modmail settings."""
        guild = ctx.guild
        muted_role_id = await self.config.guild(guild).muted_role()
        modmail_channel_id = await self.config.guild(guild).modmail_channel()
        log_channel_id = await self.config.guild(guild).log_channel()
        moderator_role_ids = await self.config.guild(guild).moderator_roles()

        muted_role = get(guild.roles, id=muted_role_id) if muted_role_id else None
        modmail_channel = guild.get_channel(modmail_channel_id) if modmail_channel_id else None
        log_channel = guild.get_channel(log_channel_id) if log_channel_id else None
        moderator_roles = [get(guild.roles, id=role_id) for role_id in moderator_role_ids]

        embed = discord.Embed(title="Modmail Settings", color=discord.Color.blue())
        embed.add_field(name="Muted Role", value=muted_role.name if muted_role else "Not Set", inline=False)
        embed.add_field(name="Modmail Channel", value=modmail_channel.mention if modmail_channel else "Not Set", inline=False)
        embed.add_field(name="Log Channel", value=log_channel.mention if log_channel else "Not Set", inline=False)
        embed.add_field(name="Moderator Roles", value=", ".join([role.name for role in moderator_roles]) if moderator_roles else "Not Set", inline=False)

        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        guild = after.guild
        muted_role_id = await self.config.guild(guild).muted_role()
        modmail_channel_id = await self.config.guild(guild).modmail_channel()
        moderator_role_ids = await self.config.guild(guild).moderator_roles()

        if not muted_role_id or not modmail_channel_id:
            return

        muted_role = get(guild.roles, id=muted_role_id)
        modmail_channel = guild.get_channel(modmail_channel_id)
        moderator_roles = [get(guild.roles, id=role_id) for role_id in moderator_role_ids]

        if not muted_role or not modmail_channel:
            return

        # Check if the muted role was added
        if muted_role not in before.roles and muted_role in after.roles:
            thread_name = f"modmail-{after.name}"
            thread = await modmail_channel.create_thread(name=thread_name, type=discord.ChannelType.private_thread)
            await thread.add_user(after)
            ping_message = f"Hello {after.mention}, this is your appeal ticket. Please explain your situation here, and a moderator will respond shortly."
            if moderator_roles:
                allowed_mentions = AllowedMentions(roles=True, users=True, everyone=False)
                ping_message = f"Hey {', '.join([role.mention for role in moderator_roles])}, there is an appeal ticket here. Please be sure to use the `.thread close` command when you are done here to close the ticket.\n" + ping_message
                await thread.send(ping_message, allowed_mentions=allowed_mentions)

            log_channel_id = await self.config.guild(guild).log_channel()
            if log_channel_id:
                log_channel = guild.get_channel(log_channel_id)
                if log_channel:
                    embed = discord.Embed(
                        title="Modmail Thread Opened",
                        description=f"A modmail thread has been created for {after.mention} in {thread.mention}.",
                        color=discord.Color.green()
                    )
                    embed.add_field(name="Thread Name", value=thread_name, inline=False)
                    embed.add_field(name="Created by", value=after.mention, inline=False)
                    await log_channel.send(embed=embed)

            async with self.config.guild(guild).thread_history() as history:
                history[after.id] = thread.id

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        guild = member.guild
        thread_history = await self.config.guild(guild).thread_history()
        thread_id = thread_history.get(member.id)

        if not thread_id:
            return

        modmail_channel_id = await self.config.guild(guild).modmail_channel()
        modmail_channel = guild.get_channel(modmail_channel_id)
        if not modmail_channel:
            return

        thread = discord.utils.get(modmail_channel.threads, id=thread_id)
        if thread:
            await thread.edit(archived=True, locked=True)

            log_channel_id = await self.config.guild(guild).log_channel()
            if log_channel_id:
                log_channel = guild.get_channel(log_channel_id)
                if log_channel:
                    embed = discord.Embed(
                        title="Modmail Thread Archived",
                        description=f"The modmail thread for {member.mention} has been archived and locked because they left the server.",
                        color=discord.Color.orange()
                    )
                    await log_channel.send(embed=embed)

            async with self.config.guild(guild).thread_history() as history:
                if member.id in history:
                    del history[member.id]

    @commands.guild_only()
    @commands.admin_or_permissions(manage_guild=True)
    @commands.command()
    async def closemodmail(self, ctx, thread: discord.Thread = None):
        """Close a modmail thread (archive and lock it)."""
        if not thread:
            thread = ctx.channel

        if not isinstance(thread, discord.Thread) or thread.owner != ctx.guild.me:
            await ctx.send("This command must be run inside a modmail thread created by me.")
            return

        await thread.edit(archived=True, locked=True, auto_archive_duration=1440)

        await ctx.send(f"Thread {thread.name} has been archived and locked. It will close within 24 hours. Mods, please do not send anymore messages in this channel.")

        log_channel_id = await self.config.guild(ctx.guild).log_channel()
        if log_channel_id:
            log_channel = ctx.guild.get_channel(log_channel_id)
            if log_channel:
                transcript = [
                    f"[{msg.created_at}] {msg.author}: {msg.content}"
                    async for msg in thread.history(limit=None)
                ]
                transcript_text = "\n".join(transcript)
                transcript_file = discord.File(fp=io.StringIO(transcript_text), filename=f"{thread.name}.txt")

                async for message in log_channel.history(limit=100):
                    if message.embeds and message.embeds[0].title == "Modmail Thread Opened" and message.embeds[0].description == f"A modmail thread has been created for {thread.owner.mention} in {thread.mention}.":
                        embed = message.embeds[0]
                        embed.title = "Modmail Thread Closed"
                        embed.description = f"Thread {thread.mention} has been closed by {ctx.author.mention}."
                        embed.color = discord.Color.red()
                        embed.set_footer(text="Ticket closed")
                        await message.edit(embed=embed)
                        break
                else:
                    embed = discord.Embed(
                        title="Modmail Thread Closed",
                        description=f"Thread {thread.mention} has been closed by {ctx.author.mention}.",
                        color=discord.Color.red()
                    )
                    await log_channel.send(embed=embed)

                await log_channel.send(file=transcript_file)

        async with self.config.guild(ctx.guild).thread_history() as history:
            user_id = next((uid for uid, tid in history.items() if tid == thread.id), None)
            if user_id:
                del history[user_id]

    @commands.guild_only()
    @commands.admin_or_permissions(manage_guild=True)
    @commands.command()
    async def threadhistory(self, ctx, user: discord.Member):
        """Retrieve past modmail threads for a user."""
        thread_history = await self.config.guild(ctx.guild).thread_history()
        thread_id = thread_history.get(user.id)

        if not thread_id:
            await ctx.send(f"No modmail thread history found for {user.mention}.")
            return

        modmail_channel_id = await self.config.guild(ctx.guild).modmail_channel()
        modmail_channel = ctx.guild.get_channel(modmail_channel_id)
        if not modmail_channel:
            await ctx.send("The modmail channel is not configured correctly.")
            return

        thread = discord.utils.get(modmail_channel.threads, id=thread_id)
        if thread:
            await ctx.send(f"Thread for {user.mention}: {thread.mention}")
        else:
            await ctx.send(f"No active thread found for {user.mention}, but it may have been archived.")
