import logging
import logging.config

import credentials
from lendbot import Lendbot

log = logging.getLogger()
log.setLevel(logging.INFO)

fh = logging.FileHandler(filename='logs/lendbot.log')
formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
fh.setFormatter(formatter)
log.addHandler(fh)

ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
log.addHandler(ch)

bot = Lendbot()
bot.run(credentials.token)
