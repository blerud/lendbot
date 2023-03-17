import discord
import openai

from credentials import openai_key

openai.api_key = openai_key

MODEL = "gpt-3.5-turbo"
PROMPT = "You are a helpful assistant."


def create_listener(bot):
    async def chat(message: discord.Message):
        if message.author.bot:
            return
        if not mentioned(bot, message):
            return

        response = retrieve_chat(message.content)
        await message.channel.send(response)

    return chat


def mentioned(bot, message: discord.Message):
    for user in message.mentions:
        if bot.user.id == user.id:
            return True
    return False


def retrieve_chat(msg: str):
    response = openai.ChatCompletion.create(
        model=MODEL, messages=[{"role": "system", "content": PROMPT}, {"role": "user", "content": msg}]
    )
    return response["choices"][0]["message"]["content"]


def setup(bot):
    bot.add_listener(create_listener(bot), 'on_message')
