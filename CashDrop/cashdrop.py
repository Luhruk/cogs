import asyncio
import datetime
import operator
import random

import aiohttp
import discord
from redbot.core import Config, bank, commands
from redbot.core.utils.predicates import MessagePredicate


class Cashdrop(commands.Cog):
    __version__ = "0.3.1"
    __author__ = "luhruk"

    def format_help_for_context(self, ctx):
        pre_processed = super().format_help_for_context(ctx)
        return f"{pre_processed}\nCog Version: {self.__version__}\nAuthor: {self.__author__}"

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=95932766180343808)
        self.config.register_guild(
            active=False,
            maths=True,
            academic=False,  # New toggle for academic questions
            chance=1,
            interval=60,
            timestamp=None,
            credits_max=550,
            credits_min=50,
            channel=None,
        )
        self.cache = {}
        self.question_bank = self.create_question_bank()  # Initialize question bank
        asyncio.create_task(self.init_loop())

    def create_question_bank(self):
        return {
            "history": [
                ("Who was the first President of the United States?", "George Washington"),
                ("In what year did World War II end?", "1945"),
            ],
            "geography": [
                ("What is the capital of France?", "Paris"),
                ("Which river is the longest in the world?", "Nile"),
            ],
            "science": [
                ("What is the chemical symbol for water?", "H2O"),
                ("What planet is known as the Red Planet?", "Mars"),
            ],
        }

    def get_academic_question(self):
        category = random.choice(list(self.question_bank.keys()))
        question, answer = random.choice(self.question_bank[category])
        return f"Category: {category.capitalize()}\n{question}", answer

    async def fetch_academic_question(self):
        """
        Fetch a random academic question from the Open Trivia Database API.
        """
        url = "https://opentdb.com/api.php?amount=1&type=multiple"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        question_data = data["results"][0]
                        question = question_data["question"]
                        correct_answer = question_data["correct_answer"]
                        return question, correct_answer
                    else:
                        return None, None
        except Exception as e:
            print(f"Error fetching question: {e}")
            return None, None

    def random_calc(self):
        ops = {
            "+": operator.add,
            "-": operator.sub,
            "*": operator.mul,
        }
        num1 = random.randint(0, 12)
        num2 = random.randint(1, 10)
        op = random.choice(list(ops.keys()))
        answer = ops.get(op)(num1, num2)
        return f"What is {num1} {op} {num2}?\n", answer

    async def init_loop(self):
        await self.bot.wait_until_ready()
        await self.generate_cache()

    def cog_unload(self):
        asyncio.create_task(self.save_triggers())

    async def generate_cache(self):
        self.cache = await self.config.all_guilds()

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or message.guild is None:
            return
        if message.guild.id not in self.cache:
            return
        guild_config = self.cache[message.guild.id]
        if not guild_config["active"]:
            return
        if random.randint(0, 100) > guild_config["chance"]:
            return
        if guild_config["timestamp"] is None:
            guild_config["timestamp"] = datetime.datetime.now(tz=datetime.timezone.utc)
        if (
            datetime.datetime.now(tz=datetime.timezone.utc)
            - guild_config["timestamp"]
        ).total_seconds() < guild_config["interval"]:
            return
        guild_config["timestamp"] = datetime.datetime.now(tz=datetime.timezone.utc)
        channel = message.channel
        if guild_config["channel"] is not None:
            channel = message.guild.get_channel(guild_config["channel"]) or message.channel

        # Default to API fetch unless academic mode is enabled
        if guild_config["academic"]:
            string, answer = self.get_academic_question()
        else:
            # Fetch a random academic question from the API
            string, answer = await self.fetch_academic_question()

        if not string or not answer:
            await channel.send("Failed to fetch a question. Please try again later.")
            return

        msg = await channel.send(string)
        try:
            pred = MessagePredicate.equal_to(str(answer), channel=channel, user=None)
            answer_msg: discord.Message = await self.bot.wait_for(
                "message", check=pred, timeout=15
            )
        except asyncio.TimeoutError:
            await msg.edit(content="Too slow!")
            return

        creds = random.randint(guild_config["credits_min"], guild_config["credits_max"])
        await msg.edit(
            content=f"Correct! {answer_msg.author.mention} got {creds} {await bank.get_currency_name(guild=message.guild)}!"
        )
        await bank.deposit_credits(answer_msg.author, creds)

    @commands.group(name="cashdrop", aliases=["cd"])
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def _cashdrop(self, ctx):
        """
        Manage the cashdrop
        """

    @_cashdrop.command(name="toggle")
    async def _toggle(self, ctx):
        """
        Toggle the cashdrop
        """
        active = await self.config.guild(ctx.guild).active()
        await self.config.guild(ctx.guild).active.set(not active)
        await ctx.send(f"Cashdrop is now {'enabled' if not active else 'disabled'}")
        await self.generate_cache()

    @_cashdrop.command(name="academic")
    async def _academic(self, ctx, toggle: bool):
        """
        Toggle academic testing mode
        """
        await self.config.guild(ctx.guild).academic.set(toggle)
        await ctx.send(f"Academic testing mode is now {'enabled' if toggle else 'disabled'}")
        await self.generate_cache()

    @_cashdrop.command(name="maths")
    async def _maths(self, ctx, toggle: bool):
        """
        Toggle maths mode
        """
        await self.config.guild(ctx.guild).maths.set(toggle)
        await ctx.send(f"Maths mode is now {'enabled' if toggle else 'disabled'}")
        await self.generate_cache()

    @_cashdrop.command(name="channel")
    async def _channel(self, ctx, channel: discord.TextChannel):
        """
        Set the channel for the cashdrop
        """
        await self.config.guild(ctx.guild).channel.set(channel.id)
        await ctx.send(f"Channel set to {channel.mention}")
        await self.generate_cache()

    @_cashdrop.command(name="chance")
    async def _chance(self, ctx, chance: int):
        """
        Set the chance percent of the cashdrop
        """
        if 0 <= chance <= 100:
            await self.config.guild(ctx.guild).chance.set(chance)
            await ctx.send(f"Chance set to {chance}%")
            await self.generate_cache()
        else:
            await ctx.send("Chance must be between 0 and 100")

    @_cashdrop.command(name="interval")
    async def _interval(self, ctx, interval: int):
        """
        Set the interval in seconds between cashdrops
        """
        if interval > 0:
            await self.config.guild(ctx.guild).interval.set(interval)
            await ctx.send(f"Interval set to {interval} seconds")
            await self.generate_cache()
        else:
            await ctx.send("Interval must be greater than 0")

    @_cashdrop.command(name="max")
    async def _max(self, ctx, max: int):
        """
        Set the max credits
        """
        if max > 0:
            min_credits = await self.config.guild(ctx.guild).credits_min()
            if max >= min_credits:
                await self.config.guild(ctx.guild).credits_max.set(max)
                await ctx.send(f"Max credits set to {max}")
                await self.generate_cache()
            else:
                await ctx.send("Max must be greater than or equal to min credits")
        else:
            await ctx.send("Max must be greater than 0")

    @_cashdrop.command(name="min")
    async def _min(self, ctx, min: int):
        """
        Set the min credits
        """
        if min > 0:
            max_credits = await self.config.guild(ctx.guild).credits_max()
            if min <= max_credits:
                await self.config.guild(ctx.guild).credits_min.set(min)
                await ctx.send(f"Min credits set to {min}")
                await self.generate_cache()
            else:
                await ctx.send("Min must be less than or equal to max credits")
        else:
            await ctx.send("Min must be greater than 0")

    @_cashdrop.command(name="addquestion")
    async def _add_question(self, ctx, category: str, question: str, answer: str):
        """
        Add a new question to the academic question bank.
        """
        valid_categories = ["history", "geography", "science"]

        if category.lower() not in valid_categories:
            await ctx.send(f"Invalid category! Please choose from: {', '.join(valid_categories)}.")
            return

        # Ensure the question and answer are not empty
        if not question or not answer:
            await ctx.send("Both question and answer must be provided.")
            return

        # Add the new question to the bank
        self.question_bank[category.lower()].append((question, answer))
        await ctx.send(f"New question added to the {category.capitalize()} category!")

    @_cashdrop.command(name="status")
    async def _status(self, ctx):
        """
        Show the current settings for Cashdrop.
        """
        guild_config = await self.config.guild(ctx.guild).all()

        status_message = (
            f"**Cashdrop Status**\n"
            f"Active: {'Enabled' if guild_config['active'] else 'Disabled'}\n"
            f"Maths Mode: {'Enabled' if guild_config['maths'] else 'Disabled'}\n"
            f"Academic Mode: {'Enabled' if guild_config['academic'] else 'Disabled'}\n"
            f"Chance: {guild_config['chance']}%\n"
            f"Interval: {guild_config['interval']} seconds\n"
            f"Min Credits: {guild_config['credits_min']}\n"
            f"Max Credits: {guild_config['credits_max']}\n"
            f"Channel: {guild_config['channel'] if guild_config['channel'] else 'Not set'}"
        )

        await ctx.send(status_message)

    @_cashdrop.command(name="testapi")
    async def _test_api(self, ctx):
        """
        Test the Open Trivia API integration.
        """
        question, answer = await self.fetch_academic_question()
        if question and answer:
            await ctx.send(f"**Question:** {question}\n**Answer:** {answer}")
        else:
            await ctx.send("API request failed or returned no data.")
