import datetime
import logging

from discord.ext import commands

import credentials
from util import config

log = logging.getLogger(__name__)

extensions = [
    'util.guild_tools',
    'ext.eightball',
    'ext.karma',
    'ext.maga',
    'ext.minecraft',
    'ext.pin',
    'ext.ping',
    'ext.poker',
    'ext.role',
    'ext.stock',
    'ext.vac',
    'ext.version',
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
