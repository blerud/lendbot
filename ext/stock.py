import logging
import re

import discord
from discord.ext import commands

from util import market

log = logging.getLogger(__name__)

tickerpattern = re.compile('\$([A-Za-z\.\^=]+)')

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
            log.warning('failed stock query \"%s\", %s', msg, str(e))

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
            f = discord.File(image, filename=symbol+'.png')
            image.close()
            await ctx.send(file=f)
        except Exception as e:
            log.warning('failed stock query \"%s\", %s', ticker, str(e))

def setup(bot):
    bot.add_listener(check_stock, 'on_message')
    bot.add_command(stock)
