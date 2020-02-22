import os
import celery
import requests
import logging
import time
import threading
import sseclient
from requests.auth import HTTPDigestAuth
from celery.signals import worker_init, worker_shutdown
from datetime import datetime, timedelta
import app.db.redis as redis
import app.db.influxdb as influxdb
from app.utils import json, dates

#Envoy access configuration
ENVOY_URL = os.environ['ENVOY_URL']
ENVOY_USERNAME = os.environ['ENVOY_USERNAME']
ENVOY_PASSWORD = os.environ['ENVOY_PASSWORD']
ENVOY_INSTALLER_USER = os.environ['ENVOY_INSTALLER_USER']
ENVOY_INSTALLER_PASS = os.environ['ENVOY_INSTALLER_PASS']

#Testing or not?
IS_TESTING = (os.environ['TEST_MODE'] == '1')

#Influxdb measurement names
INFLUXDB_INVERTER_MEAS = os.environ['INFLUXDB_INVERTER_MEAS']
INFLUXDB_METER_MEAS = os.environ['INFLUXDB_METER_MEAS']

logger = logging.getLogger('envoy_reader')
last_log = {}

#Influxdb field names
MEASUREMENT_MAPPING = {
    'p': 'active_power',
    'q': 'reactive_power',
    's': 'apparent_power',
    'v': 'voltage',
    'i': 'current',
    'f': 'frequency',
    'pf': 'power_factor'
}

PHASES = ('a','b','c')

ELEMENTS = {
    'total-consumption': 'consumption',
    'production': 'production'
}

STATE = {'processing': True}

@worker_init.connect
def init(sender=None, conf=None, **kwargs):
    redis.unlock("state:stream")
    logger.info('Unlocked [%s]' % "state:stream")

@worker_shutdown.connect
def shutdown(sender=None, conf=None, **kwargs):
    logger.info('Stopping meter read thread....')
    STATE['processing']=False

def periodic_log(name, msg, seconds):
    if not name in last_log:
        last_log[name] = datetime.now()
    current_time = datetime.now()
    if (current_time - last_log[name]).total_seconds() > seconds:
        logger.info('[%s]: %s' % (name, msg))
        last_log[name] = current_time

def sum_val(data, rkey, mkey):
    result = 0
    for phase_ele in PHASES:
        pkey = 'ph-%s' % phase_ele
        result = result + data[rkey][pkey][mkey]
    return result

@celery.task()
def write_influxdb_inverter_data(time, data):
    time = dates.from_string(time)
    data = json.loads(data)
    periodic_log('influxdb', 'writing inverter data...', 60)
    points = []
    active_count = 0
    found_producing = False
    for panel in data['inverters']:
        serial = panel['serialNumber']
        field_values = {}
        #watts
        if 'lastReportWatts' in panel:
            field_values['active_power'] = panel['lastReportWatts']
            field_values['active_power_max'] = panel['maxReportWatts']
            field_values['report_time'] = panel['lastReportDate']
        if 'producing' in panel:
            found_producing = True
            field_values['producing'] = (1 if panel['producing'] else 0)
            field_values['communicating'] = (1 if panel['communicating'] else 0)
            field_values['operating'] = (1 if panel['operating'] else 0)
            if panel['producing']:
                active_count += 1
        points.append(influxdb.point(INFLUXDB_INVERTER_MEAS, {'device': serial}, field_values, time))
    if found_producing:
        redis.set_state(redis.REDIS_ACTIVE_INVERTERS, active_count)
    if len(points) > 0:
        influxdb.write(INFLUXDB_INVERTER_MEAS, points)
    return True

@celery.task()
def write_influxdb_meter_data(time, data):
    try:
        time = dates.from_string(time)
        data = json.loads(data)
        periodic_log('influxdb', 'writing meter data...', 60)
        points = []
        for rkey in ELEMENTS.keys():
            root_ele = ELEMENTS[rkey]
            for phase_ele in PHASES:
                pkey = 'ph-%s' % phase_ele
                field_values = {}
                for mkey in MEASUREMENT_MAPPING.keys():
                    meas_ele = MEASUREMENT_MAPPING[mkey]
                    val = data[rkey][pkey][mkey]
                    field_values[meas_ele] = val
                points.append(influxdb.point(INFLUXDB_METER_MEAS, {'device': 'house', 'phase': phase_ele, 'type': root_ele}, field_values, time))
        if len(points) > 0:
            #Write determined net values
            net_values = {}
            production_values = {}
            consumption_values = {}
            for mkey in ['p','q','s']:
                meas_ele = MEASUREMENT_MAPPING[mkey]
                production = sum_val(data, 'production', mkey)
                consumption = sum_val(data, 'total-consumption', mkey)
                if mkey == 'p':
                    #Ignore error in meter readings when inverters aren't generating
                    active_inverters = redis.get_int(redis.REDIS_ACTIVE_INVERTERS, 1)
                    if active_inverters == 0 and production < 5.0:
                        production = 0.0
                net_values[meas_ele] = production - consumption
                production_values[meas_ele] = production
                consumption_values[meas_ele] = consumption
            points.append(influxdb.point(INFLUXDB_METER_MEAS, {'device': 'house', 'type': 'production', 'phase': 'all'}, production_values, time))
            points.append(influxdb.point(INFLUXDB_METER_MEAS, {'device': 'house', 'type': 'consumption', 'phase': 'all'}, consumption_values, time))
            points.append(influxdb.point(INFLUXDB_METER_MEAS, {'device': 'house', 'type': 'net', 'phase': 'all'}, net_values, time))
            influxdb.write(INFLUXDB_METER_MEAS, points)
    except:
        logger.error('Failed to write meter data.')
        logger.exception('message')
        return False
    return True

@celery.task()
def start_stream_thread():
    if not 'thread' in STATE:
        STATE['thread'] = None

    thread = STATE['thread']
    logger.info('Last update: ' + str(redis.get_state('LAST_UPDATE', default='[Not updated yet...]')))
    if redis.lock("state:stream"):
        try:
            if thread is not None:
                STATE['processing']=False
                logger.info('Waiting for previous thread to end....')
                thread.join()
                logger.info('Previous thread ended.')
            logger.info('Starting meter read thread....')
            thread = threading.Thread(target=get_stream)
            STATE['thread'] = thread
            STATE['processing']=True
            redis.unlock("state:stream")
            thread.start()
        finally:
            redis.unlock("state:stream")
    else:
        logger.error('Stream already locked for reading')

def get_stream():
    url = ENVOY_URL+'/installer/setup/home'
    try:
        if not redis.lock("state:stream"):
            logger.error('Unable to lock stream to log in')
            return
        while STATE['processing']:
            logger.info('Logging in...')
            session = requests.session()
            resp = session.get(url, auth=HTTPDigestAuth(ENVOY_INSTALLER_USER, ENVOY_INSTALLER_PASS))
            if resp.status_code != 200:
                logger.error('Login failed. Error code [%i]' % resp.status_code)
                logger.error(resp.text)
            else:
                url = ENVOY_URL+'/stream/meter'
                logger.info('Getting data from [%s]...' % url)
                resp = session.get(url, auth=HTTPDigestAuth(ENVOY_INSTALLER_USER, ENVOY_INSTALLER_PASS), stream=True, timeout=(10, 300))
                if resp.status_code == 200:
                    sclient = sseclient.SSEClient(resp)
                    logger.info('Start processing meter data...')
                    for event in sclient.events():
                        redis.set_state(redis.REDIS_METER_DATA, event.data)
                        redis.set_state('LAST_UPDATE', dates.to_string(datetime.now(dates.LOCAL_TIMEZONE)))
                        if (IS_TESTING):
                            write_influxdb_meter_data(dates.to_string(dates.utcnow()), event.data)
                        else:
                            write_influxdb_meter_data.delay(dates.to_string(dates.utcnow()), event.data)
                        if not STATE['processing']:
                            break
                    logger.info('End processing meter data...')
                else:
                    logger.error('Failed to process meter data. Error code [%i]' % resp.status_code)
                    logger.error(resp.text)
    except:
        logger.error('Failed to process meter data.')
        logger.exception('message')
    finally:
        STATE['processing'] = False
        redis.unlock("state:stream")

@celery.task()
def get_inverters():
    try:
        url = ENVOY_URL+'/inventory.json'
        logger.info('Getting data from [%s]...' % url)
        resp = requests.get(url, auth=HTTPDigestAuth(ENVOY_USERNAME, ENVOY_PASSWORD), timeout=9)
        devices = False
        if resp.status_code == 200:
            #Count active inverters
            devices = json.loads('{ "inverters": ' + resp.text + ' }')
        else:
            logger.error('Failed to get data from [%s]. Error code [%i]' % (url, resp.status_code))

        url = ENVOY_URL+'/api/v1/production/inverters'
        logger.info('Getting data from [%s]...' % url)
        resp = requests.get(url, auth=HTTPDigestAuth(ENVOY_USERNAME, ENVOY_PASSWORD), timeout=9)
        if resp.status_code == 200:
            if devices:
                readings = json.loads('{ "readings": ' + resp.text + ' }')
                for device in devices['inverters'][0]['devices']:
                    #Match reading
                    for reading in readings['readings']:
                        if str(reading['serialNumber']) == device['serial_num']:
                            device['serialNumber'] = reading['serialNumber']
                            device['lastReportDate'] = reading['lastReportDate']
                            device['lastReportWatts'] = reading['lastReportWatts']
                            device['maxReportWatts'] = reading['maxReportWatts']
                            break
            else:
                devices = readings

            data = '{ "inverters": %s }' % json.dumps(devices['inverters'][0]['devices'])
            redis.set_state(REDIS_INVERTER_DATA, data)
            if (IS_TESTING):
                write_influxdb_inverter_data(dates.to_string(dates.utcnow()), data)
            else:
                write_influxdb_inverter_data.delay(dates.to_string(dates.utcnow()), data)
        else:
            logger.error('Failed to insert new data. Error code [%i]' % resp.status_code)
    except:
        logger.error('Failed to insert new data.')
        logger.exception('message')
