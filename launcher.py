import asyncio
import logging.config
import os

import aioschedule as schedule

import credentials
from lendbot import Lendbot


async def run_scheduler():
    await schedule.run_pending()
    asyncio.get_event_loop().call_later(1, run_scheduler)


log = logging.getLogger()
log.setLevel(logging.INFO)

if not os.path.exists('logs'):
    os.makedirs('logs')
fh = logging.FileHandler(filename='logs/lendbot.log')
formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
fh.setFormatter(formatter)
log.addHandler(fh)

ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
log.addHandler(ch)

bot = Lendbot()

asyncio.get_event_loop().call_later(10, run_scheduler)
bot.run(credentials.token)
