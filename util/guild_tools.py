from typing import Optional, Tuple

from discord import Emoji, Guild, TextChannel
from discord.ext.commands import Bot

from util import config

# Global bot variable
bot: Optional[Bot] = None


def get_bot() -> Bot:
    if bot is None:
        raise ValueError("Bot not initialized yet")
    return bot


def get_default_guild() -> Guild:
    return bot.get_guild(config.default_guild)


def get_default_channel() -> TextChannel:
    return get_default_guild().get_channel(config.default_channel)


def get_emoji_str(name: str) -> str:
    emojis: Tuple[Emoji] = get_default_guild().emojis
    emoji: Optional[Emoji] = next((e for e in emojis if e.name == name), None)
    if emoji is not None:
        return "<:{}:{}>".format(emoji.name, emoji.id)
    return ":{}:".format(name)


def setup(b: Bot):
    global bot
    bot = b
