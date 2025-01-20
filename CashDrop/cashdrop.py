import asyncio
import datetime
import operator
import random
import aiohttp

import discord
from redbot.core import Config, bank, commands
from redbot.core.utils.predicates import MessagePredicate


class Cashdrop(commands.Cog):
    __version__ = "0.4.0"
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
            academic=False,  # Toggle for academic questions
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

    async def fetch_academic_question(self):
        """
        Fetch a random academic question from the Open Trivia Database API.
        """
        url = "https://opentdb.com/api.php?amount=1&type=multiple"
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

    async def get_academic_question(self):
        """
        Get an academic question, either from the API or the local question bank.
        """
        question, answer = await self.fetch_academic_question()
        if question and answer:
            return f"Category: Academic\n{question}", answer
        else:
            # Fall back to local questions if API fails
            category = random.choice(list(self.question_bank.keys()))
            question, answer = random.choice(self.question_bank[category])
            return f"Category: {category.capitalize()}\n{question}", answer

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

        if guild_config["academic"]:
            string, answer = await self.get_academic_question()
        elif guild_config["maths"]:
            string, answer = self.random_calc()
        else:
            msg = await channel.send(
                f"Some {await bank.get_currency_name(guild=message.guild)} have fallen! Type `pickup` to pick them up!"
            )
            pred = MessagePredicate.equal_to("pickup", channel=channel, user=None)
            try:
                pickup_msg: discord.Message = await self.bot.wait_for(
                    "message", check=pred, timeout=10
                )
            except asyncio.TimeoutError:
                await msg.edit(content="Too slow!")
                return
            creds = random.randint(guild_config["credits_min"], guild_config["credits_max"])
            await msg.edit(
                content=f"{pickup_msg.author.mention} picked up {creds} {await bank.get_currency_name(guild=message.guild)}!"
            )
            await bank.deposit_credits(pickup_msg.author, creds)
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

    @_cashdrop.command(name="addquestion")
    async def _add_question(self, ctx, category: str, question: str, answer: str):
        """
        Add a new question to the academic question bank.
        """
        valid_categories = ["history", "geography", "science"]

        if category.lower() not in valid_categories:
            await ctx.send(f"Invalid category! Please choose from: {', '.join(valid_categories)}.")
            return

        if not question or not answer:
            await ctx.send("Both question and answer must be provided.")
            return

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
