import discord
import inspect
import core

from discord.ext import commands


class Developer(core.Cog, command_attrs={"hidden": True}):
    def __init__(self, bot):
        self.bot = bot

    @core.group(invoke_without_command=True, aliases=["pf"])
    @commands.is_owner()
    async def profile(self, ctx):
        await ctx.send_help(ctx.command.name)

    @profile.command()
    @commands.is_owner()
    async def avatar(self, ctx, url: str = None):
        if url is None:
            if ctx.message.reference:
                ref = ctx.message.reference.resolved
                if ref.attachments:
                    url = ref.attachments[0].url
                else:
                    raise commands.MissingRequiredArgument(inspect.Parameter("url", inspect.Parameter.KEYWORD_ONLY))
            elif ctx.message.attachments:
                url = ctx.message.attachments[0].url
            else:
                raise commands.MissingRequiredArgument(inspect.Parameter("url", inspect.Parameter.KEYWORD_ONLY))

        img = await (await self.bot.session.get(url)).read()
        await self.bot.user.edit(avatar=img)
        await ctx.message.add_reaction(self.bot.icons.checkmark)

def setup(bot):
    bot.add_cog(Developer(bot))
