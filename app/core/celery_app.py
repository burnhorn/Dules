from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "dules_worker", broker=settings.REDIS_URL, backend=settings.REDIS_URL
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Seoul",
    enable_utc=True,

    worker_max_tasks_per_child=50,
    worker_max_memory_per_child=150000,     
    worker_prefetch_multiplier=1,
)

celery_app.conf.imports = ["app.worker"]
