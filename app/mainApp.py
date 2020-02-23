"""
Exposes home automation services
"""
import os
import time
import json
import logging
import logging.handlers
from functools import wraps
from flask import Flask
from flask import Response
from app.utils.crossdomain import crossdomain
from app import create_app

LOG_FILE = os.environ['LOG_FILE']

def returns_json(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        r = f(*args, **kwargs)
        return Response(r, content_type='application/json; charset=utf-8')
    return decorated_function

def returns_xml(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        r = f(*args, **kwargs)
        return Response(r, content_type='application/xml; charset=utf-8')
    return decorated_function

logger = logging.getLogger('envoy_reader')
#logger.setLevel(logging.DEBUG)
logger.setLevel(logging.INFO)
handler = logging.handlers.TimedRotatingFileHandler(LOG_FILE, when='D', interval=1, backupCount=5)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

app = create_app()
app.debug = True
celery = app.celery

from app.tasks import power
from app.requests import power

@crossdomain(origin='*')
@app.route("/")
@returns_json
def home():
    response = {}
    response['message'] = 'Welcome!'
    return json.dumps(response)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001)
