import discord
import utils
import core

from discord.ext import commands

class _HelpCommand(commands.HelpCommand):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    def get_command_signature(self, command, group_main=None):
        if group_main is not None:
            return f"{self.context.prefix}{group_main}{command.qualified_name} {command.signature}"
        else:
            return f"{self.context.prefix}{command.qualified_name} {command.signature}"

    def get_ending_note(self):
        return f"Use {self.context.prefix}{self.invoked_with} [command] for more info on a command"

    async def send_bot_help(self, mapping, used=None):
        if used:
            self.mapping = mapping

        em = discord.Embed(
            description=self.get_ending_note(),
            color=self.context.color)

        em.set_author(name=self.context.bot.user.name, icon_url=self.context.bot.user.avatar.url)

        modules = []
        for name in self.context.bot.cogs:
            cog = self.context.bot.get_cog(name)
            if not cog.qualified_name.lower() in ["jishaku"]:
                cmds = [cmd for cmd in list(cog.get_commands()) if not cmd.hidden]

                if len(cmds) > 0:
                    modules.append(cog)

        em.add_field(
            name=f"Modules [{len(modules)}]",
            value="\n".join(f"- **{cog.qualified_name}**" for cog in modules),
            inline=True
        )

        news_channel = self.context.bot.get_guild(697068320133742642).get_channel(806064505108561980)
        news_message = (await news_channel.history(limit=1).flatten())[0]
        news_content = news_message.content
        news_created = news_message.created_at.strftime('%d %b %Y')

        em.add_field(
            name=f"News [{news_created}]",
            value=news_content,
            inline=True
        )

        em.set_image(
            url="https://cdn.discordapp.com/attachments/832746281335783426/870428576804114443/proxy-image.png"
        )

        channel = self.get_destination()
        await channel.send(embed=em)

    async def send_cog_help(self, cog):
        channel = self.get_destination()
        if not await self.context.bot.is_owner(self.context.author):
            commands_ = [cmd for cmd in cog.get_commands() if cmd.hidden is False]
        else:
            commands_ = [cmd for cmd in cog.get_commands()]

        if commands_ is not None and commands_ != []:
            embed=discord.Embed(title=f"{cog.qualified_name} commands [{len(commands_)}]", description=f"{cog.description}\n\n> "+", ".join(f"`{cmd.name}`" for cmd in commands_), color=self.context.color)
            await channel.send(embed=embed)
        else:
            await channel.send("You do not have permission to view this module")

    async def send_group_help(self, group):
        channel = self.get_destination()
        if not await self.context.bot.is_owner(self.context.author) and group.hidden is True:
            return await channel.send("You do not have permission to view this group")

        group_bucket = group._buckets
        group_cooldown = group_bucket._cooldown
        if group_cooldown is not None:
            cooldown_type = list(group_bucket._type)[0]
            cooldown_per = utils.converters.time(int(group_cooldown.per), seconds=True)
            cooldown_rate = group_cooldown.rate
            cooldown_msg = f"{''.join(f'{cooldown_rate} time' if str(cooldown_rate) == '1' else f'{cooldown_rate} times')} every {cooldown_per} per {cooldown_type}"
        else:
            cooldown_msg = "1 times every 8 seconds per channel"

        if group.description is None:
            embed = discord.Embed(title=group.name, color=self.context.color)
        else:
            embed = discord.Embed(title=group.name, description=group.description, color=self.context.color)

        embed.add_field(name="Usage", value=self.get_command_signature(group, group_main=group.full_parent_name), inline=False)

        embed.add_field(name="Permissions", value=f"""
Bot: {'`Send Messages`' if len(group.extras.get('bot_perms', {})) == 0 else ', '.join(f"`{perm}`" for perm in group.extras.get('bot_perms', {}))}
User: {'`N/A`' if len(group.extras.get('bot_perms', {})) == 0 not in group.extras else '`N/A`' if len(group.extras['perms']) == 0 else ', '.join(group.extras.get('perms', {}))}
""", inline=False)

        embed.add_field(name="Cooldown", value=cooldown_msg, inline=False)

        if len(group.aliases) > 0:
            embed.add_field(name=f"Aliases [{len(group.aliases)}]", value="> " + ", ".join(f"`{alias}`" for alias in group.aliases), inline=False)

        if len(group.commands) > 0:
            embed.add_field(name=f"Subcommands [{len(group.commands)}]", value="> " + ", ".join(f"`{cmd.name}`" for cmd in group.commands), inline=False)

        embed.add_field(name="Module", value=group.cog_name)

        await channel.send(embed=embed)

    async def send_command_help(self, command):
        channel = self.get_destination()
        if not await self.context.bot.is_owner(self.context.author) and command.hidden is True:
            return await channel.send("You do not have permission to view this command")

        command_bucket = command._buckets
        command_cooldown = command_bucket._cooldown
        if command_cooldown is not None:
            cooldown_type = list(command_bucket._type)[0]
            cooldown_per = utils.converters.time(int(command_cooldown.per), seconds=True)
            cooldown_rate = command_cooldown.rate
            cooldown_msg = f"{''.join(f'{cooldown_rate} time' if str(cooldown_rate) == '1' else f'{cooldown_rate} times')} every {cooldown_per} per {cooldown_type}"
        else:
            cooldown_msg = "1 times every 8 seconds per channel"

        if command.description is None:
            embed = discord.Embed(title=command.name, color=self.context.color)
        else:
            embed = discord.Embed(title=command.name, description=command.description, color=self.context.color)

        embed.add_field(name="Usage", value=self.get_command_signature(command, group_main=command.full_parent_name))

        embed.add_field(name="Permissions", value=f"""
Bot: {'N/A' if len(command.extras.get('bot_perms', {})) == 0 else ', '.join(f"`{perm}`" for perm in command.extras.get('bot_perms', {}))}
User: {'N/A' if len(command.extras.get('bot_perms', {})) == 0 not in command.extras else '`N/A`' if len(command.extras['perms']) == 0 else ', '.join(command.extras.get('perms', {}))}
""", inline=False)

        embed.add_field(name="Cooldown", value=cooldown_msg, inline=False)

        if len(command.aliases) > 0:
            embed.add_field(name=f"Aliases [{len(command.aliases)}]", value="> " + ", ".join(f"`{alias}`" for alias in command.aliases), inline=False)

        embed.add_field(name="Module", value=command.cog_name)

        await channel.send(embed=embed)

class HelpCommand(core.Cog):
    def __init__(self, bot, help_command):
        self._original_help_command = bot.help_command
        bot.help_command = help_command(
            command_attrs={
                "hidden": True,
                "aliases": ["commands"],
                "description": "Get help on certain modules, groups or commands",
                "extras": {"bot_perms": ["Send Messages"], "perms": []}
            }
        )
        bot.help_command.cog = self

    def cog_unload(self):
        self.context.bot.help_command = self._original_help_command

def setup(bot):
    bot.add_cog(HelpCommand(bot, _HelpCommand))