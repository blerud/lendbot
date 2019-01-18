from discord.ext import commands

async def maga(message):
    if message.author.bot:
        return

    if message.content == 'maga':
        await message.channel.send('maga')

def setup(bot):
    bot.add_listener(maga, 'on_message')
