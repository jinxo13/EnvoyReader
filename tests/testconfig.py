import os
import logging

os.environ['INFLUXDB_HOST'] = 'surface.local'
os.environ['INFLUXDB_PORT'] = '8086'
os.environ['INFLUXDB_USER'] = 'writer'
os.environ['INFLUXDB_PASSWORD'] = 'writer'
os.environ['INFLUXDB_DATABASE'] = 'home'

os.environ['INFLUXDB_METER_MEAS'] = 'envoy_meter_test'
os.environ['INFLUXDB_INVERTER_MEAS'] = 'envoy_inverter_test'

os.environ['REDIS_HOST'] = 'surface.local'
os.environ['REDIS_PORT'] = '6379'
os.environ['REDIS_PASSWORD'] = ''

os.environ['LOCAL_TZ'] = 'Australia/Brisbane'

os.environ['ENVOY_URL'] = 'http://envoy.local'
os.environ['ENVOY_USERNAME'] = 'envoy'
os.environ['ENVOY_PASSWORD'] = 'XXXX'
os.environ['ENVOY_INSTALLER_USER'] = 'installer'
os.environ['ENVOY_INSTALLER_PASS'] = 'XXXX'

logger = logging.getLogger('envoy_reader')

logger.setLevel(logging.DEBUG)

handler = logging.handlers.TimedRotatingFileHandler('envoy_reader.log', when='D', interval=1, backupCount=5)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
