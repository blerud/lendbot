from discord.ext import commands

async def maga(message):
    if message.author.bot:
        return

    if message.content.lower() == 'maga':
        await message.channel.send(message.content)

def setup(bot):
    bot.add_listener(maga, 'on_message')
