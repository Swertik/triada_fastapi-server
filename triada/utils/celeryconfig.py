from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    "run_every_5_min": {
        "task": "tasks.periodic_task",
        "schedule": crontab(minute="*/1"),  # Каждые 5 минут
    }
}
