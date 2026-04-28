from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "bot_service",
    broker=str(settings.rabbitmq_url),
    backend=str(settings.redis_url)
)

celery_app.autodiscover_tasks(["app.tasks"])

import app.tasks.llm_tasks # noqa: E402,E401
