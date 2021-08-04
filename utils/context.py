from discord.ext import commands

class Context(commands.Context):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.color = int(self.bot.config["COLOR"], 16)

    async def send(self, content: str = None, reply: bool = True, *args, **kwargs):

        if content is not None:
            if len(content) > 2000:
                content = str(await self.bot.myst.post(content))

        if reply:
            return await super().reply(content, *args, **kwargs)
        return await super().send(content, *args, **kwargs)