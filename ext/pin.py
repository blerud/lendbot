import typing
from http.client import HTTPException

import discord

pin_emoji = '📌'


async def pin(reaction: discord.Reaction, user: typing.Union[discord.Member, discord.User]) -> None:
    if str(reaction.emoji) == pin_emoji:
        try:
            await reaction.message.pin()
        except HTTPException as e:
            await reaction.message.channel.send('Could not pin message, ', e)


def setup(bot) -> None:
    bot.add_listener(pin, 'on_reaction_add')
