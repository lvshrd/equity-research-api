# config/celery_config.py

from celery import Celery
from .config_load import CONFIG

celery_app = Celery(
    "tasks",
    broker=CONFIG["redis"]["url"],
    backend=CONFIG["redis"]["url"],
    include=["app.tasks"]
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    result_expires=3600 * 2,  # 2 hours cleanup
    task_acks_late=True
)