from discord.ext import commands


@commands.command()
async def availability(ctx):
    await ctx.channel.send('99.99%')


def setup(bot: commands.Bot):
    bot.add_command(availability)
