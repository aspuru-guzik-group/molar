# external
from celery import Celery

# TODO broker ? not sure what toput
celery_app = Celery("worker", broker="amqp://guest@queue//")

celery_app.conf.task_routes = {"app.worker.test_celery": "main-queue"}
