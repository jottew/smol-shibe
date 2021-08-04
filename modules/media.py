import discord
import asyncio
import utils
import core

from bs4 import BeautifulSoup
from pyppeteer import launch
from discord.ext import commands

class Browser:
    def __init__(self, *args, **kwargs):
        self.browser = None
        self.args = args
        self.kwargs = kwargs

    async def __aenter__(self):
        self.browser = await launch(
            headless=True,
            *self.args,
            **self.kwargs
        )

        return self.browser

    async def __aexit__(self, _type, val, tb):
        await self.browser.close()

class Media(core.Cog):
    def __init__(self, bot):
        self.bot = bot

    @utils.executor()
    def scrape_shibe(self, source: str):
        soup = BeautifulSoup(source, "html.parser")
        r = soup.find_all("span")
        item = list(r[23].children)[4]
        return item.get("href")

    async def get_shibe(self):
        async with Browser() as browser:
            page = await browser.newPage()
            await page.goto("https://shib.es")
            await asyncio.sleep(3)
            source = await page.content()

            url = f"http://shib.es{await self.scrape_shibe(source)}"
        return url

    @core.command(description="Fetches a shiba image from https://shib.es")
    @commands.cooldown(1,30,commands.BucketType.user)
    async def shibe(self, ctx):
        msg = await ctx.send("Fetching image from https://shib.es, this could take 3-10 seconds...")

        try:
            url = await asyncio.wait_for(
                self.get_shibe(),
                timeout=30
            )
        except asyncio.TimeoutError:
            return await ctx.send("Fetching took over 30 seconds and has therefore been cancelled")

        em = discord.Embed(color=ctx.color)
        em.set_image(url=url)
        await ctx.reply(embed=em)

def setup(bot):
    bot.add_cog(Media(bot))
