from celery import Celery
import os

celery_app = Celery(
    "metadata_celery_api",
    broker=os.getenv("RABBITMQ_BROKER"),
    backend="rpc://",
    include=["apicelery.tasks"],
)
