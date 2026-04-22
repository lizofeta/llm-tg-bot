from app.infra.celery_app import celery_app
from app.infra.redis import redis_client
from app.services.openrouter_client import openrouter_client
from app.core.enums import MessageRole

import asyncio
from pathlib import Path

system_prompt = Path("app/prompts/system_prompt.txt").read_text()

@celery_app.task(name="app.tasks.llm_tasks.llm_request")
def llm_request(
    tg_chat_id: int, 
    prompt: str
) -> None:

    messages = [
        {
            "role": MessageRole.SYSTEM,
            "content": system_prompt
        },
        {
            "role": MessageRole.USER,
            "content": prompt
        }
    ]
    
    try: 
        llm_response = openrouter_client.chat_completion(messages)

        content_llm_response = (
            llm_response
            .get("choices", [{}])[0]
            .get("message", {})
            .get("content", "Ошибка ответа LLM")
        )
    except Exception:
        content_llm_response = "Произошла ошибка при обращении к LLM"
    
    key = f"llm_result:{tg_chat_id}"

    with redis_client.pipeline() as pipe:
        pipe.rpush(
            key,
            content_llm_response
        )
        pipe.expire(key, time=600)
        pipe.execute()
