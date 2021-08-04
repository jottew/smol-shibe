import discord
import core
import re

from discord.ext import commands


class Events(core.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.REGEX = re.compile(r"::([a-zA-B1-9]{2,32})")

    @commands.Cog.listener()
    async def on_message(self, msg):
        matches = re.findall(self.REGEX, msg.content)

        if matches:
            emojis = []
            for emoji_name in matches:
                emoji = None

                for e in self.bot.emojis:
                    if e.name.lower().startswith(emoji_name.lower()):
                        emoji = e
                        break

                if emoji is not None:
                    emojis.append(str(emoji))

            if not emojis:
                return await msg.reply("No emojis found")
            
            return await msg.reply(" ".join(emojis))


def setup(bot):
    bot.add_cog(Events(bot))
