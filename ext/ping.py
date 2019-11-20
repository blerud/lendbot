import asyncio
import discord
from discord.ext import commands
import typing

class Ping(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx, group: typing.Union[discord.Member, discord.Role], delay: str):
        try:
            delay_seconds = self.get_delay_seconds(delay)
        except ValueError:
            await ctx.send('Invalid delay. Specify seconds or minutes of delay')
            return
        await asyncio.sleep(delay_seconds)
        await ctx.send(group.mention)

    def get_delay_seconds(self, delay_str):
        if delay_str.endswith('s'):
            return int(delay_str[:-1])
        else:
            return int(delay_str[:-1]) * 60

def setup(bot):
    bot.add_cog(Ping(bot))
