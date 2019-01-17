import discord
from discord.ext import commands
import re

from util import market

@commands.command()
async def stock(ctx, *args):
    if len(args) == 0:
        return
    
    ticker = args[0]
    tickerpattern = re.compile('\$([A-Za-z]+)')
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
    bot.add_command(stock)
