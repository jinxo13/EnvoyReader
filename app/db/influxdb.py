import os
from influxdb import InfluxDBClient
from datetime import datetime, timedelta
import logging
import time as tm
from dateutil import parser, tz
from app.utils import dates

client = InfluxDBClient(os.environ['INFLUXDB_HOST'], int(os.environ['INFLUXDB_PORT']), os.environ['INFLUXDB_USER'], os.environ['INFLUXDB_PASSWORD'], os.environ['INFLUXDB_DATABASE'])
logger = logging.getLogger('envoy_reader')

def point(measurement, tags, field_values, time=False):
    data = {}
    data['measurement'] = measurement
    data['tags'] = tags
    data['fields'] = field_values
    if not time:
        time = dates.utcnow()
    elif time.tzinfo is None:
        time = dates.to_utc(time)
    data['time'] = time.strftime('%Y-%m-%dT%H:%M:%SZ')
    return data

def write(measurement, points):
    logger.debug('Writing %i points to %s...' % (len(points), measurement))
    if len(points) == 0:
        return True
    retries = 3
    count = 0
    while count < retries:
        try:
            return client.write_points(points)
        except:
            logger.exception('message')
            logger.info('Retrying write...')
            tm.sleep(5)
            count = count + 1
    return False

def __get_single_meas(results):
    for measurement in results.get_points():
        time = parser.parse(measurement['time'])
        value = measurement['val']
        if value is not None:
            return {'time': time, 'value': value}
    return False

def __build_where(tags, prefix=''):
    where = ''
    for attr, value in tags.items():
        if where != '':
            where += ' and '
        where += '"%s" = \'%s\'' % (attr, value)
    if where != '':
        where = prefix + ' ' + where
    return where

def latest(measurement, tags={}, field='value', age=False):
    where = __build_where(tags, 'where')
    results = client.query('select last("%s") as val from "%s" %s;' % (field, measurement, where))
    result = __get_single_meas(results)
    if age and result:
        last_update = result['time']
        if last_update < dates.utcnow() - age:
            return False
    return result

def average(measurement, tags={}, field='value', time='1m', duration='5m'):
    where = __build_where(tags, 'and')
    results = client.query('select mean("%s") as val from "%s" where time > now() - %s %s group by time(%s) order by time desc;' % (field, measurement, duration, where, time))
    return __get_single_meas(results)

def average_period(measurement, tags={}, field='value', time='1m', from_time=False, to_time=False):
    where = __build_where(tags, 'and')
    results = []
    to_time = to_time or datetime.now()
    from_time = from_time or datetime.now()
    
    from_time = dates.to_utc(from_time).strftime('%Y-%m-%dT%H:%M:%SZ')
    to_time = dates.to_utc(to_time).strftime('%Y-%m-%dT%H:%M:%SZ')
    resp = client.query('select mean("%s") as val from "%s" where time >= \'%s\' and time < \'%s\' %s group by time(%s) order by time asc;' % (field, measurement, from_time, to_time, where, time))
    for measurement in resp.get_points():
        #Local time from UTC date/time
        time = parser.parse(measurement['time'])
        time = time.astimezone(tz.tzlocal()).replace(tzinfo=None)
        value = measurement['val']
        if value is not None:
            results.append({'time': time, 'value': value})
    return results
