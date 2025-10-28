# Celery settings
from config.env import env
from celery.schedules import crontab

CELERY_BROKER_URL = env('CELERY_BROKER_URL',default='redis://localhost:6379/1')  # Redis URL

CELERY_BEAT_SCHEDULE = {
    'update_saved_notams':{
        'task':'textprovider.tasks.update_saved_notams',
        'schedule': crontab(minute='*/5')
    } 
}