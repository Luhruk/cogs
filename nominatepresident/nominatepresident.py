import discord
from redbot.core import commands, Config
from datetime import datetime, timedelta

class PresidentCog(commands.Cog):
   def __init__(self, bot):
       self.bot = bot
       self.config = Config.get_conf(self, identifier=1234567890, force_registration=True)
       default_guild_settings = {
           "nominations": {}
       }
       self.config.register_guild(**default_guild_settings)

   @commands.command(name='nominatepresident')
   async def nominate_president(self, ctx, user: discord.User):
       guild_id = ctx.guild.id
       nominations = await self.config.guild(ctx.guild).nominations()
       nominations[msg.id] = {
           'user_id': user.id,
           'end_time': datetime.utcnow() + timedelta(hours=24)
       }
       await self.config.guild(ctx.guild).nominations.set(nominations)

       embed = discord.Embed(
           title=f'{user.name} has been nominated for president!',
           description=f'Vote with 👍 or 👎\nVoting ends in 24 hours.',
           color=0xffd700  # Gold color
       )
       embed.set_thumbnail(url=user.avatar_url)
       msg = await ctx.send(embed=embed)
       await msg.add_reaction('👍')
       await msg.add_reaction('👎')

       # Schedule task to check results after 24 hours
       self.bot.loop.create_task(self.check_results(msg.id, guild_id))

   async def check_results(self, msg_id, guild_id):
       now = datetime.utcnow()
       nominations = await self.config.guild_from_id(guild_id).nominations()
       nomination = nominations.get(msg_id)
       if nomination and now >= nomination['end_time']:
           msg = await self.bot.get_channel(ctx.channel.id).fetch_message(msg_id)
           reactions = msg.reactions
           thumbs_up = next((r for r in reactions if str(r.emoji) == '👍'), None)
           thumbs_down = next((r for r in reactions if str(r.emoji) == '👎'), None)

           if thumbs_up.count > thumbs_down.count:
               await self.process_accepted_nomination(msg, nomination['user_id'])
           else:
               await self.process_declined_nomination(msg)

           nominations.pop(msg_id)
           await self.config.guild_from_id(guild_id).nominations.set(nominations)

   async def process_accepted_nomination(self, msg, user_id):
       user = await self.bot.fetch_user(user_id)
       await msg.delete()

       embed = discord.Embed(
           title=f'{user.name} has been elected president!',
           description=f'Congratulations! Please reply with "I accept" or "I decline".',
           color=0x00ff00  # Green color
       )
       embed.set_thumbnail(url=user.avatar_url)
       reply_msg = await msg.channel.send(embed=embed)

       def check_acceptance(m):
           return m.author.id == user_id and m.content.lower() in ['i accept', 'i decline']

       try:
           reply = await self.bot.wait_for('message', check=check_acceptance, timeout=60)
           if reply.content.lower() == 'i accept':
               await self.bot.get_channel(ctx.channel.id).send(f'Congratulations, {user.name}! You are now the president.')
               # Add logic to assign the president role here
           else:
               await reply_msg.delete()
       except asyncio.TimeoutError:
           await reply_msg.delete()

   async def process_declined_nomination(self, msg):
       user_id = self.nominations[msg.id]['user_id']
       user = await self.bot.fetch_user(user_id)
       await msg.delete()

       embed = discord.Embed(
           title=f'{user.name} was not elected president.',
           description=f'Better luck next time!',
           color=0xff0000  # Red color
       )
       embed.set_thumbnail(url=user.avatar_url)
       await msg.channel.send(embed=embed)

def setup(bot):
   bot.add_cog(PresidentCog(bot))
