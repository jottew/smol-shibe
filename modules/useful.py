import discord
import utils
import core
import json
import re

from typing import Union
from discord.ext import commands

class Useful(core.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.RULES_REGEX = re.compile(r"__[\d]{1,}. (.+)__\n- (.+)")

    @core.command(aliases=["cr"], description="Pings chat revive ping")
    @utils.is_general()
    @commands.cooldown(1, 43200, commands.BucketType.guild)
    async def chatrevive(self, ctx):
        mention = f"<@&790788301266747413>"
        await ctx.send(f"{mention}, {ctx.author.mention} wants the chat to revive", allowed_mentions=discord.AllowedMentions.all())

    @core.command(aliases=["em"], description="Make the bot send an embed, this uses the json format, if you don't understand it, you can use [this](https://embedbuilder.nadekobot.me/)")
    async def embed(self, ctx, *, data: str):
        res = json.loads(data)
        em = discord.Embed().from_dict(res)
        await ctx.send(embed=em)

    @core.command(aliases=["repeat", "echo"], description="Makes the bot send a message")
    async def say(self, ctx, *, message: str):
        if len(message) > 2000:
            return await ctx.send(f"Buddy, I don't have nitro, I can't send {len(message)} character long messages")

        try:
            await ctx.message.delete()
        except:
            pass

        await ctx.send(message, reply=False)

    @core.command(aliases=["rule"], description="Get the server rules")
    async def rules(self, ctx, index: Union[int, str] = None):
        channel = self.bot.get_channel(787252501270233128)
        msg = await channel.fetch_message(787252949041938452)
        content = msg.content
        rules = self.RULES_REGEX.findall(content)

        if index is None:
            string = "\n\n".join(f"{i+1}. **{v[0]}**\n- {v[1]}" for i,v in enumerate(rules))
            em=discord.Embed(description=string, color=ctx.color)
            await ctx.send(embed=em)
        else:
            if isinstance(index, int):
                if index <= 0:
                    return await ctx.send(f"We don't have a rule {index}")

                try:
                    rule = rules[index-1]
                except IndexError:
                    return await ctx.send(f"The maximum rule index is **{len(rules)}**, if you think it should be higher, please contact staff")
            elif isinstance(index, str):
                valid = [rule for rule in rules if index.lower() in rule[0].lower()]
                if valid:
                    rule = valid[0]
                else:
                    valid = [rule for rule in rules if index.lower() in rule[1].lower()]
                    if valid:
                        rule = valid[0]
                    else:
                        return await ctx.send("No rule with that query found")
            
            title = rule[0]
            description = rule[1]
            em=discord.Embed(title=f"{rules.index(rule)+1}. {title}", description=description, color=ctx.color)
            await ctx.send(embed=em)

def setup(bot):
    bot.add_cog(Useful(bot))
