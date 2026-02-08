import unittest
from src import config

class TestConfig(unittest.TestCase):
    def test_constants_load(self):
        self.assertEqual(config.MAX_RAM_GB, 4.0)
        self.assertEqual(config.SAMPLE_RATE, 16000)
        self.assertTrue(config.IS_DEMO_MODE)
