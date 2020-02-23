import os
from celery import Celery
from flask import Flask

def make_celery(app):
    celery = Celery(
        app.import_name
    )
    celery.config_from_object('app.config.celeryconfig')

    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery

def create_app():
    app = Flask(__name__)
    os.environ['FLASK_RUN_HOST'] = '0.0.0.0'
    os.environ['FLASK_RUN_PORT'] = os.environ['APP_PORT']
    app.celery = make_celery(app)
    return app
