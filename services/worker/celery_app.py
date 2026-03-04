from celery import Celery

celery_app = Celery("worker")

celery_app.conf.update(
    broker_url="redis://localhost:6379",
    result_backend="redis://localhost:6379",
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
)

celery_app.autodiscover_tasks(["tasks"])
