import unittest
from datetime import datetime

from driver_hours_calculator.helper_functions import get_previous_sunday

class TestHelperFunctions(unittest.TestCase):
    def test_sunday_is_datetime(self):
        previous_sunday = get_previous_sunday()
        self.assertIsInstance(previous_sunday, datetime)
    
    def test_sunday_is_sunday(self):
        """
            Sunday is day 6 in python datetime.
        """
        previous_sunday = get_previous_sunday()
        self.assertEqual(previous_sunday.weekday(), 6)
