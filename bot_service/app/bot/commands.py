from aiogram import Bot
from aiogram.types import BotCommand

async def set_commands(bot: Bot):
    await bot.set_my_commands(
        [
            BotCommand(command="start", description="Начать работу"),
            BotCommand(command="help", description="Помощь по получению токена")
        ],
        language_code="ru"
    )

    await bot.set_my_commands(
        [
            BotCommand(command="start", description="Start bot"),
            BotCommand(command="help", description="How to get token")
        ],
        language_code="en"
    )
