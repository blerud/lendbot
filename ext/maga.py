from discord.ext import commands

async def maga(message):
    if message.author.bot:
        return

    if message.content.lower() == 'maga':
        i = 0
        while i < 3:
            await message.channel.send(message.content)
            ++i

def setup(bot):
    bot.add_listener(maga, 'on_message')
