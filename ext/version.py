import discord
from discord.ext import commands
import subprocess

@commands.command()
async def version(ctx):
    version = subprocess.run(['git', 'rev-parse', 'HEAD'], stdout=subprocess.PIPE).stdout.decode('utf-8')
    await ctx.channel.send(version.strip())

def setup(bot: discord.ext.commands.Bot):
    bot.add_command(version)
