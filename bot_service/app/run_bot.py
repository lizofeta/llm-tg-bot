import asyncio
from app.bot.dispatcher import bot, dp
from app.bot.redis_listener import redis_listener
from app.bot.commands import set_commands

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await set_commands(bot)
    asyncio.create_task(redis_listener(bot))
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
