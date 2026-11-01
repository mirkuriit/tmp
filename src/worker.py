from celery import Celery

from src.config import settings

celery = Celery(
    "app",
    broker=settings.redis_url,
    include=["src.event.celery_tasks"],
)