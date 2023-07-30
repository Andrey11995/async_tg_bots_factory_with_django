import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bots_factory.settings')

app = Celery('telegram_bot_LLM')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

app.conf.beat_schedule = {
    'check_last_messages_time': {
        'task': 'bots_admin.tasks.check_last_messages_time',
        'schedule': 5 * 60
    },
}
