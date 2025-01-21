import discord
from discord.ext import commands
import asyncio
import os

class ModMail(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logging_channel_id = None  # Set to the ID of the logging channel
        self.mod_role_id = None  # Set to the ID of the moderator role
        self.channel_id = None  # Set to the ID of the channel where threads will be created
        self.modmail_threads = {}  # To store active threads

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        """Triggered when a user's roles are updated."""
        if not before.roles == after.roles:
            # Check if the user was given a specific role
            if "Specific Role" in [role.name for role in after.roles]:
                await self.create_modmail_thread(after)

    async def create_modmail_thread(self, user):
        """Creates a private thread when a user is given the specific role."""
        # Create the thread in the designated channel
        channel = self.bot.get_channel(self.channel_id)
        thread = await channel.create_text_channel(
            f"modmail-{user.name}", 
            overwrites={
                channel.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                user: discord.PermissionOverwrite(read_messages=True),
                discord.utils.get(channel.guild.roles, id=self.mod_role_id): discord.PermissionOverwrite(read_messages=True),
            }
        )

        # Send the appeal message
        await thread.send(f"Hello {user.mention}, please appeal your punishment here.")

        # Log the creation of the thread
        log_channel = self.bot.get_channel(self.logging_channel_id)
        await log_channel.send(f"Modmail thread created for {user.mention} in {thread.mention}.")

        # Store the thread
        self.modmail_threads[thread.id] = {"user": user, "thread": thread}

    @commands.command()
    async def closemodmail(self, ctx):
        """Closes, locks, and archives the modmail thread."""
        thread = ctx.channel
        if thread.id not in self.modmail_threads:
            await ctx.send("This is not a modmail thread.")
            return

        # Lock and archive the thread
        await thread.edit(archived=True, locked=True)

        # Set permissions to prevent further messages
        await thread.edit(overwrites={
            ctx.guild.default_role: discord.PermissionOverwrite(send_messages=False, view_channel=False),
            self.modmail_threads[thread.id]["user"]: discord.PermissionOverwrite(read_messages=True),
            discord.utils.get(ctx.guild.roles, id=self.mod_role_id): discord.PermissionOverwrite(read_messages=True),
        })

        # Log the closing of the thread
        log_channel = self.bot.get_channel(self.logging_channel_id)
        with open(f"modmail_{thread.id}.txt", "w") as file:
            async for message in thread.history(limit=100):  # Adjust limit as needed
                file.write(f"{message.author}: {message.content}\n")

        await log_channel.send(f"Modmail thread closed for {self.modmail_threads[thread.id]['user'].mention}. Transcript saved.")

        # Remove from active threads
        del self.modmail_threads[thread.id]

    @commands.Cog.listener()
    async def on_thread_delete(self, thread):
        """Triggered when a thread is deleted."""
        if thread.id in self.modmail_threads:
            # Log the closing of the thread if not already logged
            log_channel = self.bot.get_channel(self.logging_channel_id)
            await log_channel.send(f"Modmail thread for {self.modmail_threads[thread.id]['user'].mention} was deleted.")
            del self.modmail_threads[thread.id]

def setup(bot):
    bot.add_cog(ModMail(bot))
