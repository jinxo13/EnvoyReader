from app.mainApp import app
from app.mainApp import returns_json
from app.utils.crossdomain import crossdomain
from app.db import redis
from app.utils import json

@crossdomain(origin='*')
@app.route("/power/production")
@returns_json
def production():
    result = redis.get_state(redis.REDIS_PRODUCTION_DATA, False)
    if not result:
        return json.dumps({'records': 0})
    else:
        return result

@crossdomain(origin='*')
@app.route("/power/inverter")
@returns_json
def inverter():
    result = redis.get_state(redis.REDIS_INVERTER_DATA, False)
    if not result:
        return json.dumps({'records': 0})
    else:
        return result

@crossdomain(origin='*')
@app.route("/power/stream")
@returns_json
def stream():
    result = redis.get_state(redis.REDIS_METER_DATA, False)
    if not result:
        return json.dumps({'records': 0})
    else:
        return result
