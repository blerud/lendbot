import subprocess
import discord
from discord.ext import commands


class VersionCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="version", description="Get the current version of the bot")
    async def version(self, ctx: discord.ApplicationContext):
        version = subprocess.run(['git', 'show', '-s', '--format=%h %s'], stdout=subprocess.PIPE).stdout.decode('utf-8')
        await ctx.respond(version.strip())


def setup(bot):
    bot.add_cog(VersionCog(bot))
