import discord
from discord.channel import TextChannel
from discord.ext import commands
from discord.ext.commands import Context
import requests
import schedule

from util import config, guild_tools

client = None


async def check_vac_status(url):
    request = requests.get(url=url)
    return '<div class="profile_ban">' in request.text


class Vac(commands.Cog):

    def __init__(self):
        try:
            with open(config.vac_file, 'r') as f:
                self.urls = [url for url in f]
        except FileNotFoundError:
            self.urls = []

    @commands.group()
    async def vac(self, ctx: Context):
        """VAC ban status checker."""
        if ctx.invoked_subcommand is None:
            await self.check_vac_status_and_send_results(ctx.channel, True)

    @vac.command(name='list')
    async def list0(self, ctx: Context):
        """List current profiles to be checked"""
        if len(self.urls) != 0:
            await ctx.channel.send('\n'.join(['{}. <{}>'.format(i, url) for i, url in enumerate(self.urls)]))
        else:
            await ctx.channel.send("No profiles registered to checker.")

    @vac.command(name='add')
    async def add(self, ctx: Context, url: str):
        """Add a profile to the checker"""
        if url not in self.urls:
            self.urls.append(url)
            self.write_vac()
            await ctx.channel.send("Registered <{}> to checker.".format(url))
        else:
            await ctx.channel.send("<{}> is already registered to checker.".format(url))

    @vac.command(name='remove')
    async def remove(self, ctx: Context, url: str):
        """Remove a profile to the checker by index or url"""
        try:
            index = int(url)
            if 0 <= index < len(self.urls):
                removed_url = self.urls[index]
                del self.urls[index]
                self.write_vac()
                await ctx.channel.send("Removed <{}> from checker.".format(removed_url))
            else:
                await ctx.channel.send("{} is not a valid index.".format(index))
        except ValueError:
            if url in self.urls:
                self.urls.remove(url)
                self.write_vac()
                await ctx.channel.send("Removed <{}> from checker.".format(url))
            else:
                await ctx.channel.send("<{}> is not registered to checker.".format(url))

    @vac.command(name='check')
    async def check(self, ctx: Context, url: str):
        """Manually check a profile for a ban. Can provide an index or a url."""
        try:
            index = int(url)
            if 0 <= index < len(self.urls):
                url = self.urls[index]
            else:
                await ctx.channel.send("{} is not a valid index.".format(index))
                return
        except ValueError:
            pass

        if await check_vac_status(url):
            await ctx.channel.send("<{}> is VAC banned! {}".format(url, guild_tools.get_emoji_str('poggers')))
        else:
            await ctx.channel.send("<{}> is not banned {}".format(url, guild_tools.get_emoji_str('angry')))

    def write_vac(self):
        with open(config.vac_file, 'w+') as f:
            f.writelines(self.urls)

    async def check_vac_status_and_send_results(self, channel: TextChannel, send_if_no_results: bool):
        response = []
        for url in self.urls:
            if await check_vac_status(url):
                response.append(
                    "<{}> is VAC banned! {} Removing from checker.".format(url, guild_tools.get_emoji_str('poggers')))
                self.urls.remove(url)

        self.write_vac()

        if len(response) != 0:
            await channel.send('\n'.join(response))
        elif send_if_no_results:
            await channel.send("No banned players found {}".format(guild_tools.get_emoji_str('angry')))


def setup(bot: discord.ext.commands.Bot):
    global client
    client = bot
    vac = Vac()
    bot.add_cog(vac)

    channel = bot.get_channel(int(config.default_channel))

    def job():
        vac.check_vac_status_and_send_results(channel, True)

    schedule.every().day.at("12:00").do(job)
