from app.infra.celery_app import celery_app
from app.infra.redis import sync_redis_client
from app.services.openrouter_client import openrouter_client
from app.core.enums import MessageRole

from pathlib import Path
import json

system_prompt = Path("app/prompts/system_prompt.txt").read_text()

@celery_app.task
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
    

    sync_redis_client.rpush(
            "llm_queue",
            json.dumps(
                {
                    "chat_id": tg_chat_id,
                    "text": content_llm_response
                }
            )
        )
    sync_redis_client.expire("llm_queue", time=600)
