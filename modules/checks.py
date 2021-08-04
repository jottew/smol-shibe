import discord
import core

from discord.ext import commands


class Checks(core.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.add_check(self.cooldown)
        self.cdm = commands.CooldownMapping.from_cooldown(1, 5, commands.BucketType.user)

    async def cooldown(self, ctx):
        if await self.bot.is_owner(ctx.author):
            return True
        bucket = self.cdm.get_bucket(ctx.message)
        retry_after = bucket.update_rate_limit()
        if retry_after:
            raise commands.CommandOnCooldown(bucket, retry_after, bucket)
        return True

def setup(bot):
    bot.add_cog(Checks(bot))
