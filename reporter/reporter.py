import discord
from discord.ext import commands
from discord.ext.commands import has_permissions

class Reporter(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.forum_channel = None
        self.role_name = None
        self.locked_threads = {}
        print("[DEBUG] Reporter cog initialized. Commands should now be registered.")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.guild is None and not message.author.bot:
            if self.locked_threads.get(message.author.id):
                await self.create_forum_thread(message.author)
            else:
                await self.forward_message_to_thread(message)

    @commands.command()
    @has_permissions(administrator=True)
    async def reporter_set_forum_channel(self, ctx: commands.Context, channel: discord.TextChannel):
        """Set the forum channel where threads will be created."""
        print("[DEBUG] reporter_set_forum_channel command triggered.")
        self.forum_channel = channel
        await ctx.send(f"Forum channel set to {channel.mention}")
        print(f"[DEBUG] Forum channel set to: {channel.name} ({channel.id})")

    @commands.command()
    @has_permissions(manage_roles=True)
    async def reporter_set_role(self, ctx: commands.Context, role: discord.Role):
        """Set the role that will be pinged in the forum thread."""
        print("[DEBUG] reporter_set_role command triggered.")
        self.role_name = role.name
        await ctx.send(f"Role for notifications set to {role.name}")
        print(f"[DEBUG] Role set to: {role.name} ({role.id})")

    async def create_forum_thread(self, user: discord.User):
        """Create a private forum thread for the user."""
        if not self.forum_channel:
            return await user.send("No forum channel has been set by the moderators.")

        print(f"[DEBUG] Creating thread for user: {user.name} ({user.id})")

        thread = await self.forum_channel.create_text_channel(
            name=f"{user.name}-{user.id}",
            overwrites={
                self.forum_channel.guild.default_role: discord.PermissionOverwrite(view_channel=False),
                user: discord.PermissionOverwrite(view_channel=True),
            },
        )

        embed = discord.Embed(
            title=f"User Profile - {user.name}",
            description=(
                f"User ID: {user.id}\n"
                f"Account Created: {user.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"Joined Server: {user.joined_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"Roles: {', '.join([role.name for role in user.roles if role.name != '@everyone'])}"
            ),
            color=discord.Color.blue(),
        )
        embed.set_thumbnail(url=user.avatar.url if user.avatar else None)
        await thread.send(embed=embed)

        if self.role_name:
            role = discord.utils.get(self.forum_channel.guild.roles, name=self.role_name)
            if role:
                await thread.send(f"Ping: {role.mention}")
                print(f"[DEBUG] Pinged role: {role.name} ({role.id})")

        self.locked_threads[user.id] = thread

    async def forward_message_to_thread(self, message: discord.Message):
        """Forward a message to the user's forum thread."""
        thread = self.locked_threads.get(message.author.id)
        if thread:
            embed = discord.Embed(description=message.content, color=discord.Color.green())
            embed.set_footer(text=f"User ID: {message.author.id}")
            await thread.send(embed=embed)

    @commands.command()
    @has_permissions(administrator=True)
    async def reporter_close(self, ctx: commands.Context):
        """Close and lock a forum thread."""
        print("[DEBUG] reporter_close command triggered.")
        if ctx.channel.id in [t.id for t in self.locked_threads.values()]:
            self.locked_threads[ctx.channel.id] = True
            await ctx.send("Thread has been closed and locked.")
        else:
            await ctx.send("This thread cannot be closed.")

    @commands.command()
    async def reporter_reopen(self, ctx: commands.Context):
        """Reopen a previously closed forum thread."""
        print("[DEBUG] reporter_reopen command triggered.")
        if ctx.channel.id in self.locked_threads and self.locked_threads[ctx.channel.id]:
            self.locked_threads[ctx.channel.id] = False
            await ctx.send("Thread has been reopened.")
        else:
            await ctx.send("This thread is already open.")

# Ensure the cog is properly loaded
async def setup(bot: commands.Bot):
    print("[DEBUG] Setting up Reporter cog...")
    await bot.add_cog(Reporter(bot))
    print("[DEBUG] Reporter cog loaded successfully.")
    print(f"[DEBUG] Registered commands: {', '.join([command.name for command in bot.commands])}")
