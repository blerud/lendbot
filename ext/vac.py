import json

import aioschedule as schedule
import discord
import requests
from discord.channel import TextChannel
from discord.ext import commands
from discord.ext.commands import Context

from util import config, guild_tools

client = None


async def check_vac_status(url):
    request = requests.get(url=url)
    return '<div class="profile_ban">' in request.text


class Vac(commands.Cog):
    def __init__(self):
        try:
            with open(config.vac_file, "r") as f:
                vac_json = json.load(f)
                self.banned_urls = vac_json["banned_urls"]
                self.urls = vac_json["urls"]
        except FileNotFoundError:
            self.banned_urls = []
            self.urls = []

    @commands.group()
    async def vac(self, ctx: Context):
        """VAC ban status checker."""
        if ctx.invoked_subcommand is None:
            await self.check_vac_status_and_send_results(ctx.channel, True)

    @vac.command(name="list")
    async def list0(self, ctx: Context):
        """List current profiles to be checked"""
        if len(self.urls) != 0:
            await ctx.channel.send("\n".join(["{}. <{}>".format(i + 1, url) for i, url in enumerate(self.urls)]))
        else:
            await ctx.channel.send("No profiles registered to checker.")

    @vac.command(name="banned")
    async def banned(self, ctx: Context):
        """List profiles that have been banned."""
        if len(self.banned_urls) != 0:
            await ctx.channel.send("\n".join(["{}. <{}>".format(i + 1, url) for i, url in enumerate(self.banned_urls)]))
        else:
            await ctx.channel.send("No profiles have been banned.")

    @vac.command(name="add")
    async def add(self, ctx: Context, url: str):
        """Add a profile to the checker"""
        if url not in self.urls:
            self.urls.append(url)
            self.write_vac()
            await ctx.channel.send("Registered <{}> to checker.".format(url))
        else:
            await ctx.channel.send("<{}> is already registered to checker.".format(url))

    @vac.command(name="remove")
    async def remove(self, ctx: Context, url: str):
        """Remove a profile to the checker by index or url"""
        try:
            index = int(url)
            if 0 < index <= len(self.urls):
                removed_url = self.urls[index - 1]
                del self.urls[index - 1]
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

    def write_vac(self):
        with open(config.vac_file, "w") as f:
            json.dump({"banned_urls": self.banned_urls, "urls": self.urls}, f)

    async def check_vac_status_and_send_results(self, channel: TextChannel = None, send_if_no_results: bool = False):
        response = []
        banned = []
        for url in self.urls:
            if await check_vac_status(url):
                poggers = guild_tools.get_emoji_str("poggers")
                if not banned:
                    csgo_mention = f"@&{config.csgo_id}"
                    response.append("<{}> players have been banned {})".format(csgo_mention, poggers))
                response.append("<{}> is VAC banned! {} Removing from checker.".format(url, poggers))
                banned.append(url)
                self.banned_urls.append(url)
        for url in banned:
            self.urls.remove(url)
        self.write_vac()

        if channel is None:
            channel = client.get_channel(int(config.default_channel))

        if len(response) != 0:
            await channel.send("\n".join(response))
        elif send_if_no_results:
            await channel.send("No banned players found {}".format(guild_tools.get_emoji_str("angry")))


def setup(bot: discord.ext.commands.Bot):
    global client
    client = bot
    vac = Vac()
    bot.add_cog(vac)

    async def job():
        await vac.check_vac_status_and_send_results()

    schedule.every().hour.do(job)
