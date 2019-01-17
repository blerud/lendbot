import credentials
from lendbot import Lendbot

bot = Lendbot()
bot.run(credentials.token)
