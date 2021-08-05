import asyncio
import logging.config
import os
import traceback

import aioschedule as schedule

import credentials
from lendbot import Lendbot


async def start_scheduler():
    await asyncio.sleep(10)
    await run_scheduler()


async def run_scheduler():
    try:
        await schedule.run_pending()
    except Exception:
        print(traceback.format_exc())
    await asyncio.sleep(1)
    asyncio.get_running_loop().create_task(run_scheduler())


log = logging.getLogger()
log.setLevel(logging.INFO)

if not os.path.exists('logs'):
    os.makedirs('logs')
fh = logging.handlers.RotatingFileHandler('logs/lendbot.log', maxBytes=10000, backupCount=5)
formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
fh.setFormatter(formatter)
log.addHandler(fh)

ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
log.addHandler(ch)

bot = Lendbot()

asyncio.get_event_loop().create_task(start_scheduler())
bot.run(credentials.token)
