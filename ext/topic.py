import datetime
import logging
import typing

from discord.ext import commands

log = logging.getLogger(__name__)


@commands.group()
async def topic(ctx: commands.Context):
    pass


@topic.command(name='append')
async def append(ctx: commands.Context, s: str):
    topic = ctx.channel.topic
    if topic is None:
        await set_topic(ctx, s)
    else:
        new_topic = topic + ' ' + s
        await set_topic(ctx, new_topic)


@topic.command(name='set')
async def set_(ctx: commands.Context, s: str):
    await set_topic(ctx, s)


async def set_topic(ctx: commands.Context, new_topic: str):
    try:
        await ctx.channel.edit(topic=new_topic, reason=reason(ctx.message.author.name, ctx.channel.topic))
    except Exception as e:
        log.warn(e)
        print(e)


def reason(user: str, prev: typing.Optional[str]) -> str:
    if prev is None:
        prev = ''
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return f'Edit made by {user} at {timestamp}. Previous value: \"{prev}\"'


def setup(bot: commands.Bot):
    bot.add_command(topic)
