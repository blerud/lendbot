import discord
from discord.ext import commands
import re

from util import market

tickerpattern = re.compile('\$([A-Za-z\.]+)')

async def check_stock(message):
    if message.author.bot:
        return

    msg = message.content
    if msg.startswith('$'):
        try:
            symbol = tickerpattern.match(msg)
            if symbol:
                price = market.get_stock_price(symbol.group(1))
                pricefmt = '{0:,.2f}'.format(price)
                await message.channel.send('$' + str(pricefmt))
        except Exception as e:
            print('failed stock query ', msg)
            print(e)

@commands.command()
async def stock(ctx, *args):
    if len(args) == 0:
        return
    
    ticker = args[0]
    symbolmatch = tickerpattern.match(ticker)
    if symbolmatch:
        try:
            symbol = symbolmatch.group(1)
            image = market.get_intraday_graph(symbol)
            f = discord.File(image.read(), filename=symbol+'.png')
            image.close()
            await ctx.send(file=f)
        except Exception as e:
            print('failed stock query ', symbol)
            print(e)

def setup(bot):
    bot.add_listener(check_stock, 'on_message')
    bot.add_command(stock)
