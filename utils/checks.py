from discord.ext import commands

def is_general():
    def predicate(ctx):
        channel = 845243855648456734
        if ctx.channel.id != channel:
            raise commands.CheckFailure(f"This command is only for <#{channel}>")
        return True
    
    return commands.check(predicate)