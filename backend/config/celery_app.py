import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('medical_chatbot')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# Periodic tasks for Antifragile system
app.conf.beat_schedule = {
    'process-feedback-hourly': {
        'task': 'apps.feedback.tasks.process_feedback',
        'schedule': crontab(minute=0),  # Every hour
    },
    'retrain-rag-weekly': {
        'task': 'apps.feedback.tasks.retrain_rag_pipeline',
        'schedule': crontab(hour=2, minute=0, day_of_week=0),  # Sunday 2 AM
    },
    'update-causal-graph-weekly': {
        'task': 'apps.feedback.tasks.update_causal_graph',
        'schedule': crontab(hour=3, minute=0, day_of_week=0),  # Sunday 3 AM
    },
}
