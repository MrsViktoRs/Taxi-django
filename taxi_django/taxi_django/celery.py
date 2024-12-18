from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab
import logging

logger = logging.getLogger(__name__)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'taxi_django.settings')

app = Celery('taxi_django')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'send-report-every-single-minute': {
        'task': 'main_app.tasks.send_messages',
        'schedule': crontab(),
    },
}

