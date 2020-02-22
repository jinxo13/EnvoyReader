import tests.testconfig
import unittest
import time
from app.tasks import power

class streamTest(unittest.TestCase):
    
    def setUp(self):
        pass

    def testStream(self):
        power.init()
        power.start_stream_thread()
        time.sleep(60)
        power.shutdown()
        