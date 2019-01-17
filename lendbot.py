import discord
from discord.ext import commands
import asyncio
import datetime
import re

from util import market

import config
import credentials

extensions = [
    'ext.stock'
]

class Lendbot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=config.prefix)

        self.client_id = credentials.client_id

        self.add_listener(self.check_stock, 'on_message')

        for extension in extensions:
            try:
                self.load_extension(extension)
                print('loaded', extension)
            except Exception as e:
                print('failed to load ', extension)
    
    async def on_ready(self):
        self.ontime = datetime.datetime.utcnow()
        print('logged in')

    async def check_stock(self, message):
        if message.content == 'maga':
            await message.channel.send('maga')
            return
        
        if message.author == self.user:
            return

        msg = message.content
        if msg.startswith('$'):
            try:
                tickerpattern = re.compile('\$([A-Za-z\.]+)')
                symbol = tickerpattern.match(msg)
                if symbol:
                    price = market.get_stock_price(symbol.group(1))
                    await message.channel.send('$' + str(price))
            except Exception as e:
                print('failed stock query ', msg)
                print(e)
