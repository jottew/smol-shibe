import asyncio

from core.main import bot

try:
    bot.run(bot.config.get("TOKEN"))
except (KeyboardInterrupt):
    asyncio.run(bot.close())