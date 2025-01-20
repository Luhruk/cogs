import discord
from discord.ext import commands
from discord.ext.commands import has_permissions
import datetime


class Reporter(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.forum_channel = None  # Will hold the forum channel for creating threads
        self.locked_threads = {}  # Dictionary to track locked threads

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.guild is None and not message.author.bot:  # This is a direct message
            if self.locked_threads.get(message.author.id):
                # Create a new thread if locked
                await self.create_forum_thread(message.author)
            else:
                await self.forward_message_to_thread(message)

    @commands.command()
    @has_permissions(administrator=True)
    async def reporter_set_forum_channel(self, ctx, channel: discord.TextChannel):
        """Sets the forum channel where threads will be created."""
        self.forum_channel = channel
        await ctx.send(f"Forum channel set to {channel.mention}")

    async def create_forum_thread(self, user):
        """Creates a forum thread when a DM is received."""
        if not self.forum_channel:
            return await user.send("No forum channel has been set by the moderators.")

        # Create a forum thread
        thread = await self.forum_channel.create_text_channel(
            name=f"{user.name}-{user.id}",
            overwrites={
                self.forum_channel.guild.default_role: discord.PermissionOverwrite(view_channel=False),
                user: discord.PermissionOverwrite(view_channel=True)
            }
        )

        # Create the embed with the user's profile information
        embed = discord.Embed(
            title=f"User Profile - {user.name}",
            description=(
                f"User ID: {user.id}\n"
                f"Account Created: {user.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"Joined Server: {user.joined_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"Roles: {', '.join([role.name for role in user.roles if role.name != '@everyone'])}"
            ),
            color=discord.Color.blue()
        )
        embed.set_thumbnail(url=user.avatar.url if user.avatar else None)
        await thread.send(embed=embed)

        # Ping the specified role (this should be set by moderators)
        role = discord.utils.get(self.forum_channel.guild.roles, name="YourRoleName")  # Replace with dynamic role
        if role:
            await thread.send(f"Ping: {role.mention}")

        # Store the thread for future message forwarding
        self.locked_threads[user.id] = thread

    async def forward_message_to_thread(self, message):
        """Forwards the user's message to the appropriate forum thread."""
        thread = self.locked_threads.get(message.author.id)
        if thread:
            embed = discord.Embed(
                description=message.content,
                color=discord.Color.green()
            )
            embed.set_footer(text=f"User ID: {message.author.id}")
            await thread.send(embed=embed)

    @commands.command()
    @has_permissions(administrator=True)
    async def reporter_close(self, ctx):
        """Closes a thread by locking it."""
        if ctx.channel.id in [t.id for t in self.locked_threads.values()]:
            self.locked_threads[ctx.channel.id] = True
            await ctx.send("Thread has been closed and locked.")
        else:
            await ctx.send("This thread cannot be closed.")

    @commands.command()
    async def reporter_reopen(self, ctx):
        """Reopens a locked thread."""
        if ctx.channel.id in self.locked_threads and self.locked_threads[ctx.channel.id]:
            self.locked_threads[ctx.channel.id] = False
            await ctx.send("Thread has been reopened.")
        else:
            await ctx.send("This thread is already open.")


async def setup(bot):
    await bot.add_cog(Reporter(bot))
