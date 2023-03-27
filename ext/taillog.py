import subprocess

from discord.ext import commands

FILENAME = "logs/stdout-stderr"


@commands.command()
async def taillog(ctx, n: int = 10):
    logs = tail(FILENAME, n).strip()
    await ctx.send("```\n" + logs + "\n```")


def tail(filename, n):
    return subprocess.run(["tail", "-n", str(n), filename], stdout=subprocess.PIPE).stdout.decode('utf-8')


def setup(bot):
    bot.add_command(taillog)
