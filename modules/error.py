from operator import is_not
import discord
import utils
import core

from discord.ext import commands


class Errors(core.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandInvokeError):
            error = error.original

        if isinstance(error, commands.CommandNotFound):
            return
        
        if isinstance(error, commands.CommandOnCooldown):
            return await ctx.send(f"This command is on cooldown, please try again in {utils.converters.time(int(error.retry_after*1000))}")

        return await ctx.send(f"{error.__class__.__name__}: {str(error)}")

def setup(bot):
    bot.add_cog(Errors(bot))
