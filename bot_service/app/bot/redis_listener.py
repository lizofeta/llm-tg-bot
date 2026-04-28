import json

from aiogram import Bot
from app.infra.redis import redis_client

async def redis_listener(bot: Bot):
    while True:
        _, data = await redis_client.blpop("llm_queue")
        
        payload = json.loads(data)

        await bot.send_message(
            chat_id=payload["chat_id"],
            text=payload["text"]
        )
