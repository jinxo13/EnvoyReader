import redis
import logging
import os

#Collections
REDIS_METER_DATA = 'envoy.meter.stream'
REDIS_INVERTER_DATA  = 'envoy.inverter'
REDIS_ACTIVE_INVERTERS = 'envoy.inverters.active'

redis_host = os.environ['REDIS_HOST']
redis_port = int(os.environ['REDIS_PORT'])
redis_password = os.environ['REDIS_PASSWORD']

redis_client = redis.StrictRedis(host=redis_host, port=redis_port, password=redis_password)
logger = logging.getLogger('envoy_reader')

def get_state(name, default=False):
    if redis_client.exists(name):
        return redis_client.get(name)
    return default

def get_int(name, default=0):
    return int(get_state(name, default))

def set_state(name, value):
    redis_client.set(name, value)

def lock(name):
    state = get_state(name)
    if state == b'1':
        return False
    set_state(name, b'1')
    return True

def unlock(name):
    set_state(name, b'0')

def publish(topic, data):
    redis_client.publish(topic, data)

def subscribe(topic):
    p = redis_client.pubsub()
    p.subscribe(topic)
    return p
