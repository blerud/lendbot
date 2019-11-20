import discord
from discord.ext import commands
import asyncio
import datetime
import logging
import re

import config
import credentials

log = logging.getLogger(__name__)

extensions = [
    'ext.maga',
    'ext.stock',
    'ext.role',
    'ext.eightball',
    'ext.poker',
    'ext.minecraft',
    'ext.ping',
]

class Lendbot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=config.prefix)

        self.client_id = credentials.client_id

        for extension in extensions:
            try:
                self.load_extension(extension)
                log.info('loaded %s', extension)
            except Exception as e:
                log.warning('failed to load %s', extension)
                raise e

    async def on_ready(self):
        self.ontime = datetime.datetime.utcnow()
        log.info('logged in')
