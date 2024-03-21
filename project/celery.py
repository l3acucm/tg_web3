from __future__ import absolute_import, unicode_literals

import os

import django
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

app = Celery('project')
app.conf.broker_url = f"amqp://{os.environ.get('RABBITMQ_USER')}:{os.environ.get('RABBITMQ_PASSWORD')}@{os.environ.get('RABBITMQ_HOST')}:5672/{os.environ.get('RABBITMQ_VHOST')}"
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'listen_contract': {
        'task': 'project.smart_contracts_listener.tasks.write_new_events',
        'schedule': 1
    },
    'publish_reports': {
        'task': 'project.smart_contracts_listener.tasks.build_and_publish_report',
        'schedule': 4 * 60 * 60
    },
}

app.autodiscover_tasks()
