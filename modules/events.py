import imagehash
import core
import re

from PIL import Image
from io import BytesIO
from discord.ext import commands


class Events(core.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.REGEX = re.compile(r"::([a-zA-B1-9]{2,32})")
        self.images = []

    @commands.Cog.listener("on_message")
    async def similar(self, msg):
        if msg.channel.id != 722249103794372648:
            return

        if not msg.attachments:
            return

        for attachment in msg.attachments:            
            img = Image.open(BytesIO(await attachment.read()))
            hash = imagehash.average_hash(img)

            sent = False
            for i in self.images:
                if (i - hash) < 5:
                    if not sent:
                        await msg.reply("Repost bad!!!")
                        sent = True
            if not sent:
                self.images.append(hash)
            img.close()

    @commands.Cog.listener("on_message")
    async def emojis(self, msg):
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
