from aiogram import Bot, Dispatcher
from app.core.config import settings
from app.bot.handlers import router

bot = Bot(token=settings.telegram_bot_token)

dp = Dispatcher()

dp.include_router(router)
