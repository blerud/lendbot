import discord
from discord.ext import commands
import json
import re
import typing

pattern = re.compile('(\+\+|--)\s*(\d+)?$')

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

        # Write karma_dict to disk if changes
        if recipients != 0:
            self.write_to_file(self._filename, self.karma_dict)

        # Send out responses
        response = []
        sender = message.author.display_name
        for member in recipients:
            receiver = member.display_name
            total = self.karma_dict[str(member.id)]
            await message.channel.send("{} {}'d {} (now at {})".format(sender, karma_verb, receiver, total))

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
