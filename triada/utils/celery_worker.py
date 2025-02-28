import time

from celery import Celery
from celery.schedules import crontab

celery_app = Celery(
    "worker",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0",
)

celery_app.conf.update(
    CELERYBEAT_SCHEDULE={
        'periodic_task_every_5_minutes': {
            'task': 'triada.utils.celery_worker.periotic_task',
            'schedule': crontab(minute='*/1'),
        },
    },
    CELERY_TIMEZONE='UTC',
)


@celery_app.task
def periotic_task():
    print('ААААААА ЖЕНЩИНААА')
    return "ЖЕНЩИНА ПОВЕРЖЕНА"
