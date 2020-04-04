import asyncio
import logging.config
import os
import traceback
from datetime import datetime

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
filename = datetime.now().strftime('logs/lendbot_%Y.%m.%d-%H.%M.%S.log')
fh = logging.FileHandler(filename=filename)
formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
fh.setFormatter(formatter)
log.addHandler(fh)

ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
log.addHandler(ch)

bot = Lendbot()

asyncio.get_event_loop().create_task(start_scheduler())
bot.run(credentials.token)
