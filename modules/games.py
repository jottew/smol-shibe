import difflib
import inspect
import discord
import random
import asyncio
import core
import time
import re

from typing import List, Dict, Any
from discord.ext import commands
from aiohttp import ClientResponse
from collections import namedtuple

Typerace = namedtuple("typerace", "winners texts message")

class Typerace:
    def __init__(self, winners: list, texts: tuple, message: discord.Message = None) -> None:
        self.winners: List[Dict[str, Any]] = winners
        self.texts: tuple = texts
        self.message: discord.Message = message

class Games(core.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.words: List[str] = []
        self.typeraces: List[Typerace] = []
        self.typerace_emojis: List[str] = ["🥇", "🥈", "🥉"]

    async def _setup(self):
        resp: ClientResponse = await self.bot.session.get(
            "https://gist.githubusercontent.com/deekayen/4148741/raw/98d35708fa344717d8eee15d11987de6c8e26d7d/1-1000.txt"
        )
        text: str = await resp.text()
        self.words: List[str] = text.splitlines()

    def encrypt_text(self, text: str) -> str:
        chars: Dict[list] = self.bot.config.SIMILARS
        return "".join(
            char
            if char not in chars.keys()
            else random.choice(chars.get(char))
            for char in text
        )

    def decrypt_text(self, text: str) -> str:
        chars: Dict[list] = self.bot.config.SIMILARS
        for k, v in chars.items():
            for char in v:
                text = text.replace(char, k)
        return text

    async def get_text(self, amount: int) -> str:
        if not self.words:
            await self._setup()
        words = [
            random.choice(self.words)
            for _ in range(amount)
        ]
        text = " ".join(words)
        return (text, self.encrypt_text(text))

    def format_line(self, emoji: str, winner: Dict[str, Any]) -> str:
        return f"{emoji} | " \
            f"{winner['user'].mention} in {winner['time']:.2f}s | " \
            f"**WPM:** {winner['wpm']:.2f} | " \
            f"**Accuracy:** {winner['accuracy']:.2f}%"

    async def add_winner(self, me: Typerace):
        embed = me.message.embeds[0]
        if len(me.winners) == 1:
            embed.add_field(
                name="Winners",
                value=self.format_line(self.typerace_emojis[len(me.winners)-1], me.winners[len(me.winners)-1])
            )
        else:
            embed.fields[0].value += self.format_line(self.typerace_emojis[len(me.winners)-1], me.winners[len(me.winners)-1])
        await me.message.edit(embed=embed)

    class TyperaceFlags(commands.FlagConverter, prefix='--', delimiter=' '):
        words: int = 16
        timeout: int = 30

    # credit to https://github.com/Tom-the-Bomb/Discord-Games cuz i stole some code :)
    @core.group(invoke_without_command=True, aliases=["tr"])
    @commands.max_concurrency(1, per=commands.BucketType.channel)
    async def typerace(self, ctx, *, flags: TyperaceFlags):
        words = flags.words
        timeout = flags.timeout

        if words > 128:
            return await ctx.send("You can't have more than 128 words")
        if words < 1:
            return await ctx.send("You can't have less than 1 word")
        if timeout < 0:
            return await ctx.send("The timeout can't be negative")

        original, text = await self.get_text(words)

        self.typeraces.append(
            Typerace(
                [],
                (original, text)
            )
        )
        me = self.typeraces[len(self.typeraces)-1]

        code = len(self.typeraces)
        embed = discord.Embed(
            title="Typerace",
            description="`"*3+text+"`"*3,
            color=ctx.color
        )
        embed.set_footer(text=f"Typerace {code}")

        me.message = await ctx.send(embed=embed)
        start = time.perf_counter()

        def check(m: discord.Message) -> bool:
            content = m.content.lower().replace("\n", " ")
            if m.channel == ctx.channel and not m.author.bot and m.author not in map(lambda m: m["user"], me.winners):
                sim = difflib.SequenceMatcher(None, content, original).ratio()
                return sim >= 0.9

        while True:
            try:
                msg: discord.Message = await self.bot.wait_for(
                    "message",
                    check=check,
                    timeout=timeout
                )
            except asyncio.TimeoutError:
                if me.winners:
                    break
                else:
                    return await me.message.edit("No one responded, the game has therefore timed out.", embed=None)

            end = time.perf_counter()
            content = msg.content.lower()
            timeout -= round(end - start)

            me.winners.append({
                "user": msg.author, 
                "time": end - start, 
                "wpm" : len(text.split(" ")) / ((end - start) / 60), 
                "accuracy" : difflib.SequenceMatcher(None, content, text).ratio() * 100
            })

            
            await self.add_winner(me)
            await msg.add_reaction(self.typerace_emojis[len(me.winners)-1])

            if len(me.winners) >= 3:
                break

        desc = [self.format_line(self.typerace_emojis[i-1], x) for i, x in enumerate(me.winners, 1)]
        embed = discord.Embed(
            title="Typerace Results",
            description=f"""
The text was:
```
{original}
```
""",
            color=ctx.color
        )
        embed.add_field(name="Winners", value="\n".join(desc))
        await ctx.reply(embed=embed)
        del self.typeraces[code-1]

    @typerace.command(name="decrypt", aliases=["d", "solve", "s"])
    @commands.is_owner()
    async def typerace_decrypt(self, ctx, *, text: str):
        await ctx.author.send(self.decrypt_text(text))
        await ctx.send("Decrypted text sent to DMs")

    @typerace.command(name="win", aliases=["w"])
    @commands.is_owner()
    async def typerace_win(self, ctx, code: int = None):
        typerace_reg = re.compile(r"Typerace (?P<number>\d)")
        if ctx.message.reference or code:
            if code is None:
                ref = ctx.message.reference.resolved
                if ref.author.id != self.bot.user.id or not ref.embeds or not ref.embeds[0].footer or not typerace_reg.match(ref.embeds[0].footer.text):
                    raise commands.MissingRequiredArgument(inspect.Parameter("message", inspect.Parameter.KEYWORD_ONLY))
                code = int(typerace_reg.match(ref.embeds[0].footer.text).group("number"))
            typerace = self.typeraces[code-1]
            typerace.winners.append({
                "user": ctx.author, 
                "time": 0, 
                "wpm" : 99999, 
                "accuracy" : 99.9
            })
            await self.add_winner(typerace)
            await ctx.message.add_reaction("✅")
        else:
            raise commands.MissingRequiredArgument(inspect.Parameter("message", inspect.Parameter.KEYWORD_ONLY))

def setup(bot):
    bot.add_cog(Games(bot))
