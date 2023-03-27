from typing import List

import discord
from discord.ext import commands
import openai

from credentials import openai_key

openai.api_key = openai_key

MODEL = "gpt-3.5-turbo"
GPT4_MODEL = "gpt-4"
NAME = "assistant"
PROMPT = "You are a helpful assistant."
CONTEXT = 10
RESET_HISTORY = ".reset"


class Chat(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.model = MODEL
        self.prompt = PROMPT
        self.name = NAME

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        if not self.mentioned(message):
            return

        async with message.channel.typing():
            history = await self.retrieve_history(message.channel)
            response = self.retrieve_chat(message, history)
            await message.channel.send(response)

    def mentioned(self, message: discord.Message):
        for user in message.mentions:
            if self.bot.user.id == user.id:
                return True
        return False

    async def retrieve_history(self, channel):
        context = []
        async for message in channel.history(limit=CONTEXT):
            context.insert(0, message)
        reset_index = 0
        for i, message in enumerate(context):
            if RESET_HISTORY in message.content:
                reset_index = i
        reset_index += 1
        return context[reset_index:-1]

    def retrieve_chat(self, msg: discord.Message, history: List[discord.Message]):
        messages = [{"role": "system", "content": self.prompt}]
        for message in history:
            if message.content is None or len(message.content) == 0:
                continue
            messages.append(self.create_openai_message(message))
        messages.append(self.create_openai_message(msg))
        response = openai.ChatCompletion.create(model=self.model, messages=messages)
        return self.trim_response(response["choices"][0]["message"]["content"])

    def create_openai_message(self, message: discord.Message):
        role = "assistant" if message.author.id == self.bot.user.id else "user"
        user = self.name if message.author.id == self.bot.user.id else message.author.display_name
        content = f"{user}: {self.replace_name(message.clean_content)}"
        return {"role": role, "content": content}

    def replace_name(self, msg):
        return msg.replace(self.bot.user.display_name, self.name)

    def trim_response(self, msg):
        if msg.startswith(self.name + ":"):
            return msg.replace(self.name + ":", "")
        return msg.lstrip()

    @commands.command(name="model")
    async def change_model(self, ctx, arg):
        self.model = arg
        await ctx.send(f"Model set to \"{self.model}\"")

    @commands.command()
    async def reset_model(self, ctx):
        self.model = MODEL
        await ctx.send(f"Model reset to \"{self.model}\"")

    @commands.command(name="gpt4")
    async def gpt4(self, ctx):
        self.model = GPT4_MODEL
        await ctx.send(f"Model set to \"{self.model}\"")

    @commands.command(name="prompt")
    async def change_prompt(self, ctx, *args):
        self.prompt = " ".join(args)
        await ctx.send(f"Prompt set to \"{self.prompt}\"")

    @commands.command()
    async def reset_prompt(self, ctx):
        self.prompt = PROMPT
        await ctx.send(f"Prompt reset to \"{self.prompt}\"")

    @commands.command(name="name")
    async def change_name(self, ctx, *args):
        self.name = " ".join(args)
        await ctx.send(f"Name set to \"{self.name}\"")

    @commands.command()
    async def reset_name(self, ctx):
        self.name = NAME
        await ctx.send(f"Name reset to \"{self.name}\"")


def setup(bot):
    chat = Chat(bot)
    bot.add_cog(chat)
