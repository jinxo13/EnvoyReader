import os
from datetime import timedelta
from kombu import Queue
from celery.schedules import crontab
from app.config.schedule import ScheduleOffset

BROKER_TRANSPORT = 'redis'
BROKER_URL = 'redis://%s:%i' % (os.environ['REDIS_HOST'], int(os.environ['REDIS_PORT']))
CELERY_RESULT_BACKEND = BROKER_URL

CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

#CELERY_IMPORTS = ('app.tasks')

CELERY_TASK_RESULT_EXPIRES = 30

#CELERY_ROUTES = {'app.tasks.power.get_stream': {'queue': 'meter_stream'}}

CELERYBEAT_SCHEDULE = {
    'power-panels': {
        'task': 'app.tasks.power.get_inverters',
        # Every 2 minutes
        'schedule': ScheduleOffset(timedelta(seconds=300), timedelta(seconds=60)),
        'options': {
            'expires': 300
        }
    },

    'power-stream': {
        'task': 'app.tasks.power.start_stream_thread',
        # Every 1 minute
        'schedule': 60,
        'options': {
            'expires': 60
        }
    },

}
