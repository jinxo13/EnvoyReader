import tests.testconfig
import unittest
from app import utils
from app.db import influxdb
from datetime import timedelta, datetime
from app.utils import dates

class dbTests(unittest.TestCase):
    
    PHASE_A = {'type': 'production', 'device': 'house', 'phase': 'a'}
    HOUSE_NET = {'type': 'net', 'device': 'house'}

    def setUp(self):
        points = []
        points.append(influxdb.point('power_test', dbTests.HOUSE_NET, {'active_power': 1.1}))
        points.append(influxdb.point('power_test', dbTests.PHASE_A, {'active_power': 1.2}))
        influxdb.write(points)

    def testGetLatest(self):
        val = influxdb.latest('power_test', dbTests.HOUSE_NET, 'active_power')
        print(val)

        val = influxdb.latest('power_test', dbTests.HOUSE_NET, 'active_power', timedelta(minutes=5))
        print(val)

    def testAverage(self):
        val = influxdb.average('power_test', dbTests.PHASE_A, 'active_power')
        print(val)

    def testAveragePeriod(self):
        val = influxdb.average_period('power_test', dbTests.PHASE_A, 'active_power', from_time=datetime.now(dates.LOCAL_TIMEZONE)-timedelta(minutes=10))
        start_date = utils.dates.local_day_start()
        val = influxdb.average_period('power_meter', dbTests.HOUSE_NET, 'active_power', from_time=start_date)
        print(val)
