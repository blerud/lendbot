from typing import List

import discord
import openai

from credentials import openai_key

openai.api_key = openai_key

MODEL = "gpt-3.5-turbo"
NAME = "lendbot"
PROMPT = f"You are a {NAME}, helpful assistant."
CONTEXT = 10
RESET_HISTORY = ".reset"


def create_listener(bot):
    async def chat(message: discord.Message):
        if message.author.bot:
            return
        if not mentioned(bot, message):
            return

        history = await retrieve_history(message.channel)
        response = retrieve_chat(message, history, bot)
        await message.channel.send(response)

    return chat


def mentioned(bot, message: discord.Message):
    for user in message.mentions:
        if bot.user.id == user.id:
            return True
    return False


async def retrieve_history(channel):
    context = []
    async for message in channel.history(limit=CONTEXT):
        context.insert(0, message)
    reset_index = 0
    for i, message in enumerate(context):
        if RESET_HISTORY in message.content:
            reset_index = i
    reset_index += 1
    return context[reset_index:-1]


def retrieve_chat(msg: discord.Message, history: List[discord.Message], bot):
    messages = [{"role": "system", "content": PROMPT}]
    for message in history:
        if message.content is None or len(message.content) == 0:
            continue
        messages.append(create_openai_message(message, bot))
    messages.append(create_openai_message(msg, bot))
    response = openai.ChatCompletion.create(model=MODEL, messages=messages)
    return trim_response(response["choices"][0]["message"]["content"])


def create_openai_message(message: discord.Message, bot):
    role = "assistant" if message.author.id == bot.user.id else "user"
    user = NAME if message.author.id == bot.user.id else message.author.display_name
    content = f"{user}: {replace_name(message.clean_content, bot)}"
    return {"role": role, "content": content}


def replace_name(msg, bot):
    return msg.replace(bot.user.display_name, NAME)


def trim_response(msg):
    if msg.startswith(NAME + ":"):
        return msg.replace(NAME + ":", "")
    return msg.lstrip()


def setup(bot):
    bot.add_listener(create_listener(bot), 'on_message')
