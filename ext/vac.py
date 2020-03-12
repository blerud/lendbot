import discord
from discord.ext.commands import Context
from discord.channel import TextChannel
from discord.ext import commands
import requests
import schedule
from typing import Union
from .. import config

client = None


class Vac(commands.Cog):

    def __init__(self):
        try:
            with open(config.vac_file, 'r') as f:
                self.urls = [url for url in f]
        except FileNotFoundError:
            self.urls = []

    @commands.group()
    async def vac(self, ctx: Context):
        """VAC ban status checker"""
        await self.check_vac_status_and_send_results(ctx.channel, True)

    @vac.command(name='list')
    async def list0(self, ctx: Context):
        """List current profiles to be checked"""
        await ctx.channel.send('\n'.join(['{}. {}'.format(i, url) for i, url in enumerate(self.urls)]))

    @vac.command
    async def add(self, ctx: Context, url: str):
        """Add a profile to the checker"""
        if url not in self.urls:
            self.urls.append(url)
            self.write_vac()
            await ctx.channel.send("Registered {} to checker.".format(url))
        else:
            await ctx.channel.send("{} is already registered to checker.".format(url))

    @vac.command
    async def remove(self, ctx: Context, url: Union[str, int]):
        """Remove a profile to the checker by index or url"""
        if type(url) == int:
            if 0 <= url < len(self.urls):
                removed_url = self.urls[url]
                del self.urls[url]
                await ctx.channel.send("Removed {} from checker.".format(removed_url))
            else:
                await ctx.channel.send("{} is not a valid index.".format(url))
        else:
            if url in self.urls:
                self.urls.remove(url)
                self.write_vac()
                await ctx.channel.send("Removed {} from checker.".format(url))
            else:
                await ctx.channel.send("{} is not registered to checker.".format(url))

    def write_vac(self):
        with open(config.vac_file, 'w+') as f:
            f.writelines(self.urls)

    async def check_vac_status_and_send_results(self, channel: TextChannel, send_if_no_results: bool):
        response = []
        for url in self.urls:
            request = requests.get(url=url)
            if '<div class="profile_ban">' in request.text:
                response.append(url + " is VAC banned! Removing from checker.")

        if len(response) != 0:
            await channel.send('\n'.join(response))
        elif send_if_no_results:
            await channel.send('No banned players found :angry-1:')


def setup(bot: discord.ext.commands.Bot):
    global client
    client = bot
    vac = Vac()
    bot.add_cog(vac)

    channel = bot.get_channel(int(config.default_channel))

    def job():
        vac.check_vac_status_and_send_results(channel, False)

    schedule.every().day.at("12:00").do(job)
