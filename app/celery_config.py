# app/celery_config.py
from celery import Celery
import toml

Redis_config = toml.load("config.toml")["REDIS"]

celery = Celery(
    "tasks",

    broker=Redis_config["REDIS_URL"],
    backend=Redis_config["REDIS_URL"],
    include=["app.tasks"]
)

celery.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"]
)