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
            "moderator_role": None,
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
        await ctx.send(f"Muted role set to {role.name}.", allowed_mentions=discord.AllowedMentions.none())

    @modmailset.command()
    async def modmailchannel(self, ctx, channel: discord.TextChannel):
        """Set the channel where modmail threads will be created."""
        await self.config.guild(ctx.guild).modmail_channel.set(channel.id)
        await ctx.send(f"Modmail channel set to {channel.mention}.", allowed_mentions=discord.AllowedMentions.none())

    @modmailset.command()
    async def logchannel(self, ctx, channel: discord.TextChannel):
        """Set the channel where modmail logs will be sent."""
        await self.config.guild(ctx.guild).log_channel.set(channel.id)
        await ctx.send(f"Log channel set to {channel.mention}.", allowed_mentions=discord.AllowedMentions.none())

    @modmailset.command()
    async def moderatorrole(self, ctx, role: discord.Role):
        """Set the role to be pinged in modmail threads."""
        await self.config.guild(ctx.guild).moderator_role.set(role.id)
        await ctx.send(f"Moderator role set to {role.name}.", allowed_mentions=discord.AllowedMentions.none())

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        guild = after.guild
        muted_role_id = await self.config.guild(guild).muted_role()
        modmail_channel_id = await self.config.guild(guild).modmail_channel()
        moderator_role_id = await self.config.guild(guild).moderator_role()

        if not muted_role_id or not modmail_channel_id:
            return

        muted_role = get(guild.roles, id=muted_role_id)
        modmail_channel = guild.get_channel(modmail_channel_id)
        moderator_role = get(guild.roles, id=moderator_role_id) if moderator_role_id else None

        if not muted_role or not modmail_channel:
            return

        # Check if the muted role was added
        if muted_role not in before.roles and muted_role in after.roles:
            thread_name = f"modmail-{after.name}"
            thread = await modmail_channel.create_thread(name=thread_name, type=discord.ChannelType.private_thread)
            await thread.add_user(after)
            ping_message = f"Hello {after.mention}, this is your appeal ticket. Please explain your situation here, and a moderator will respond shortly."
            if moderator_role:
                allowed_mentions = AllowedMentions(roles=True, users=True, everyone=False)
                ping_message = f"Hey {moderator_role.mention}, there is an appeal ticket here.\n" + ping_message
                await thread.send(ping_message, allowed_mentions=allowed_mentions)

            # Log the creation and save to thread history
            log_channel_id = await self.config.guild(guild).log_channel()
            if log_channel_id:
                log_channel = guild.get_channel(log_channel_id)
                if log_channel:
                    await log_channel.send(
                        f"A modmail thread has been created for {after.mention} in {thread.mention}."
                    )
            async with self.config.guild(guild).thread_history() as history:
                history.setdefault(after.id, []).append(thread.id)

    @commands.guild_only()
    @commands.admin_or_permissions(manage_guild=True)
    @commands.command()
    async def closemodmail(self, ctx, thread: discord.Thread = None):
        """Close and lock a modmail thread."""
        if not thread:
            thread = ctx.channel

        if not isinstance(thread, discord.Thread) or thread.owner != ctx.guild.me:
            await ctx.send("This command must be run inside a modmail thread created by me.", allowed_mentions=discord.AllowedMentions.none())
            return

        # Close the thread (like clicking 'Close Thread' in Discord)
        await thread.close()

        # Archive and lock the thread (optional, depending on your use case)
        await thread.edit(archived=True, locked=True)

        await ctx.send(f"Thread {thread.name} has been closed and locked.", allowed_mentions=discord.AllowedMentions.none())

        # Log the closure and save a .txt transcript
        log_channel_id = await self.config.guild(ctx.guild).log_channel()
        if log_channel_id:
            log_channel = ctx.guild.get_channel(log_channel_id)
            if log_channel:
                transcript = [f"[{msg.created_at}] {msg.author}: {msg.content}" async for msg in thread.history(limit=100)]  # Limiting to 100 messages
                transcript_text = "\n".join(transcript)
                transcript_file = discord.File(fp=io.StringIO(transcript_text), filename=f"{thread.name}.txt")
                await log_channel.send(f"Thread {thread.name} was closed by {ctx.author.mention}.", file=transcript_file)

        # Remove thread from history
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
        thread_ids = thread_history.get(user.id)

        if not thread_ids:
            await ctx.send(f"No modmail thread history found for {user.mention}.", allowed_mentions=discord.AllowedMentions.none())
            return

        modmail_channel_id = await self.config.guild(ctx.guild).modmail_channel()
        modmail_channel = ctx.guild.get_channel(modmail_channel_id)
        if not modmail_channel:
            await ctx.send("The modmail channel is not configured correctly.", allowed_mentions=discord.AllowedMentions.none())
            return

        threads = [discord.utils.get(modmail_channel.threads, id=tid) for tid in thread_ids]
        threads_mentions = [f"{thread.mention}" if thread else "Archived thread" for thread in threads]
        await ctx.send(f"Threads for {user.mention}: {', '.join(threads_mentions)}", allowed_mentions=discord.AllowedMentions.none())
