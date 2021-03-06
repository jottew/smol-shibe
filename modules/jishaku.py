import jishaku
import psutil
import sys
import discord
import humanize

from discord.ext import commands
from jishaku.features.baseclass import Feature
from jishaku.modules import package_version
from jishaku.cog import STANDARD_FEATURES, OPTIONAL_FEATURES

jishaku.Flags.HIDE = True
jishaku.Flags.NO_DM_TRACEBACK = True
jishaku.Flags.NO_UNDERSCORE = True

class Jishaku(*OPTIONAL_FEATURES, *STANDARD_FEATURES):

    @Feature.Command(name="jishaku", aliases=["jsk"], invoke_without_command=True, ignore_extra=False, hidden=True)
    async def jsk(self, ctx: commands.Context):
        """
        The Jishaku debug and diagnostic commands.
        This command on its own gives a status brief.
        All other functionality is within its subcommands.
        """

        summary = [
            f"Jishaku v{package_version('jishaku')}, discord.py `{package_version('discord.py')}`, "
            f"`Python {sys.version}` on `{sys.platform}`".replace("\n", ""),
            f"Module was loaded <t:{self.load_time.timestamp():.0f}:R>, "
            f"cog was loaded <t:{self.start_time.timestamp():.0f}:R>.",
            ""
        ]

        # detect if [procinfo] feature is installed
        if psutil:
            try:
                proc = psutil.Process()

                with proc.oneshot():
                    try:
                        mem = proc.memory_full_info()
                        summary.append(f"Using `{humanize.naturalsize(mem.rss)}` physical memory and "
                                       f"`{humanize.naturalsize(mem.vms)}` virtual memory, "
                                       f"`{humanize.naturalsize(mem.uss)}` of which unique to this process.")
                    except psutil.AccessDenied:
                        pass

                    try:
                        name = proc.name()
                        pid = proc.pid
                        thread_count = proc.num_threads()

                        summary.append(f"Running on PID {pid} (`{name}`) with {thread_count} thread{''.join('s' if thread_count > 1 else '')}.")
                    except psutil.AccessDenied:
                        pass

                    summary.append("")  # blank line
            except psutil.AccessDenied:
                summary.append(
                    "psutil is installed, but this process does not have high enough access rights "
                    "to query process information."
                )
                summary.append("")  # blank line

        cache_summary = f"`{len(self.bot.guilds)}` guild{''.join('s' if len(self.bot.guilds) > 1 else '')} and `{len(self.bot.users)}` user{''.join('s' if len(self.bot.users) > 1 else '')}"

        # Show shard settings to summary
        if isinstance(self.bot, discord.AutoShardedClient):
            if len(self.bot.shards) > 20:
                summary.append(
                    f"This bot is automatically sharded (`{len(self.bot.shards)}` shards of `{self.bot.shard_count}`)"
                    f" and can see {cache_summary}."
                )
            else:
                shard_ids = ', '.join(str(i) for i in self.bot.shards.keys())
                summary.append(
                    f"This bot is automatically sharded (Shards `{shard_ids}` of `{self.bot.shard_count}`)"
                    f" and can see {cache_summary}."
                )
        elif self.bot.shard_count:
            summary.append(
                f"This bot is manually sharded (Shard `{self.bot.shard_id}` of `{self.bot.shard_count}`)"
                f" and can see {cache_summary}."
            )
        else:
            summary.append(f"This bot is not sharded and can see {cache_summary}.")

        # pylint: disable=protected-access
        if self.bot._connection.max_messages:
            message_cache = f"Message cache capped at `{self.bot._connection.max_messages}`"
        else:
            message_cache = "Message cache is `disabled`"

        if discord.version_info >= (1, 5, 0):
            presence_intent = f"presence intent is `{'enabled' if self.bot.intents.presences else 'disabled'}`"
            members_intent = f"members intent is `{'enabled' if self.bot.intents.members else 'disabled'}`"

            summary.append(f"{message_cache}, {presence_intent}\n{members_intent}.")
        else:
            guild_subscriptions = f"guild subscriptions are `{'enabled' if self.bot._connection.guild_subscriptions else 'disabled'}`"

            summary.append(f"{message_cache} and {guild_subscriptions}.")

        # pylint: enable=protected-access

        # Show websocket latency in milliseconds
        summary.append(f"Average websocket latency: `{round(self.bot.latency * 1000, 2)}`ms")

        embed = discord.Embed(description="\n".join(summary), color=ctx.color)
        embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar.url)

        await ctx.send(embed=embed)


def setup(bot: commands.Bot):
    bot.add_cog(Jishaku(bot=bot))