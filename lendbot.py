import discord
from discord.ext import commands
import asyncio
import datetime
import re

import config
import credentials

extensions = [
    'ext.maga',
    'ext.stock'
]

class Lendbot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=config.prefix)

        self.client_id = credentials.client_id

        for extension in extensions:
            try:
                self.load_extension(extension)
                print('loaded', extension)
            except Exception as e:
                print('failed to load ', extension)
    
    async def on_ready(self):
        self.ontime = datetime.datetime.utcnow()
        print('logged in')
