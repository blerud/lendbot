from discord.ext import commands
from riotwatcher import LolWatcher, ApiError
from time import time
import json
import typing
import discord

from discord.ext.commands import Context

key = 'RGAPI-ea5ee892-d481-4c2f-8972-e24abed3b763'
watcher = LolWatcher(key)


class Lol(commands.Cog):
    _filename = 'lol.json'

    def __init__(self):
        self.lol_dict = self.load_from_file(self._filename)

    @commands.group()
    async def lol(self, ctx: Context):
        """LoL summoner checker"""
        if ctx.invoked_subcommand is None:
            await ctx.send(
                '''```.lol add [user] [summonername]
.lol daysclean [user]
.lol list [user]```'''
            )

    @lol.command(name='daysclean')
    async def daysclean(self, ctx: Context, user: discord.Member):
        """Checks user's summoner names for days since last game."""
        key = str(user.id)
        if key not in self.lol_dict:
            await ctx.send("User has no registered summoner names")
            return

        names = self.lol_dict[key]
        days = None

        for name in names:
            summoner = watcher.summoner.by_name('na1', name)

            try:
                matches = watcher.match.matchlist_by_account('na1', summoner['accountId'], ['420'], None, None, 0, 1)
                recent_match = matches['matches'][0]
                timestamp_diff = (time() * 1000) - recent_match['timestamp']
                days_diff = int(timestamp_diff / (1000 * 60 * 60 * 24))
                if days is None or days_diff > days:
                    days = days_diff
            except ApiError:
                await ctx.send("Error retrieving recent matches")
                return

        if days is None:
            await ctx.send("{0} has never played ranked".format(user))
        else:
            await ctx.send("{0} has been clean for {1} days".format(user, days))

    @lol.command(name='add')
    async def add(self, ctx, user: discord.Member, summonername: str):
        """Add user's summoner name to LoL list."""
        key = str(user.id)
        if key not in self.lol_dict:
            self.lol_dict[key] = []

        self.lol_dict[key].append(summonername)
        self.write_to_file(self._filename, self.lol_dict)
        await ctx.send("{0}: {1}".format(user, self.lol_dict[key]))

    @lol.command(name='list')
    async def list0(self, ctx, user: discord.Member):
        """List user's summoner names."""
        key = str(user.id)
        if key not in self.lol_dict:
            await ctx.send("User has no registered summoner names")
            return
        await ctx.send("{0}: {1}".format(user, self.lol_dict[key]))

    @lol.command(name='remove')
    async def remove(self, ctx, user: discord.Member, summonername: str):
        """Remove user's summoner names from LoL list."""
        key = str(user.id)
        if key in self.lol_dict:
            del self.lol_dict[key]
            self.write_to_file(self._filename, self.lol_dict)

    def load_from_file(self, filename: str) -> typing.Dict[str, int]:
        try:
            with open(filename, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def write_to_file(self, filename: str, lol: typing.Dict[str, int]) -> None:
        with open(filename, 'w+') as f:
            json.dump(lol, f)


def setup(bot):
    bot.add_cog(Lol())
