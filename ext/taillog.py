import subprocess
from discord.ext import commands

FILENAME = "logs/stdout-stderr"


class TaillogCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="taillog", description="Get the last n lines of the log file")
    async def taillog(self, ctx, n: int = 10):
        logs = self.tail(FILENAME, n).strip()
        await ctx.respond("```\n" + logs + "\n```")

    def tail(self, filename, n):
        return subprocess.run(["tail", "-n", str(n), filename], stdout=subprocess.PIPE).stdout.decode('utf-8')


def setup(bot):
    bot.add_cog(TaillogCog(bot))
