import unittest
from influxdb import InfluxDBClient

class retagTests(unittest.TestCase):

    def point(self, measurement, tags, field_values):
        data = {}
        data['measurement'] = measurement
        data['tags'] = tags
        data['fields'] = field_values
        data['time'] = field_values['time']
        return data

    def testMe(self):
        return
        client = InfluxDBClient('pi3.local', 8086, 'writer', 'writer', 'home')
        results = client.query('select * from home.store_perm.power_net')
        points = []
        for measurement in results.get_points():
            pt = self.point('power', {'device': 'house', 'phase': 'all', 'type':'net'}, measurement)
            if isinstance(measurement['active_power'], float) \
                and isinstance(measurement['apparent_power'], float) \
                and isinstance(measurement['reactive_power'], float):
                points.append(pt)
            if len(points) == 1000:
                print('Write 1000 points...')
                client.write_points(points)
                points = []
        print('Write %i points...' % len(points))                
        client.write_points(points)
