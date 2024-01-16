# celeryconfig.py
from datetime import timedelta

CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERYBEAT_SCHEDULE = {
    'cleanup-task': {
        'task': 'app.cleanup_task',
        'schedule': timedelta(minutes=5),  # Adjust the interval as needed
    },
}
