from discord.ext import commands
import discord


class AvailabilityCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="availability", description="Get the availability percentage")
    async def availability(self, ctx: discord.ApplicationContext):
        await ctx.respond('99.999%')


def setup(bot):
    bot.add_cog(AvailabilityCog(bot))
