import json
import re
import typing

import discord
from discord.ext import commands

pattern = re.compile('(\+\+|--)$')


class Karma(commands.Cog):
    _filename = 'karma.txt'

    def __init__(self):
        self.karma_dict = self.load_from_file(self._filename)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        match = pattern.search(message.content)
        if match == None:
            return

        # Update karma_dict
        karma_verb = match.groups()[0]
        karma_change = 1 if karma_verb == '++' else -1

        recipients = [m for m in message.mentions if m != message.author]
        for member in recipients:
            key = str(member.id)
            self.karma_dict[key] = self.karma_dict.get(key, 0) + karma_change

        if len(recipients) != 0:
            # Write karma_dict to disk
            self.write_to_file(self._filename, self.karma_dict)

            # Send out responses
            sender = message.author.display_name
            response = [
                "{} {}'d {} (now at {})".format(sender, karma_verb, member.display_name,
                                                self.karma_dict[str(member.id)])
                for member in recipients
            ]
            await message.channel.send('\n'.join(response))

    @commands.command()
    async def karma(self, ctx: discord.ext.commands.Context, member: discord.Member):
        if str(member.id) in self.karma_dict:
            nick = member.nick if member.nick is not None else member.name
            await ctx.send('{} karma: {}'.format(nick, self.karma_dict[str(member.id)]))

    def load_from_file(self, filename: str) -> typing.Dict[str, int]:
        try:
            with open(filename, 'r') as f:
                return json.load(f)
        except FileNotFoundError as e:
            return {}

    def write_to_file(self, filename: str, karma: typing.Dict[str, int]) -> None:
        with open(filename, 'w+') as f:
            json.dump(karma, f)


def setup(bot: discord.ext.commands.Bot):
    bot.add_cog(Karma())
