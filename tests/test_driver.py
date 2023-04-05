#PYTHON
import unittest
#3RD PARTY
import pandas as pd
#LOCAL

from driver_hours_calculator.fleets import Fleet
from driver_hours_calculator.driver import Driver, AllDrivers

class TestDriver(unittest.TestCase):
    #SINGLE DRIVER TESTS
    def test_driver_code_is_string(self):
        driver = Driver('Test', 'California')
        self.assertIsInstance(driver.code, str)

    def test_assigned_fleet_is_a_fleet(self):
        driver = Driver('Test', 'California')
        fleet = driver.fleet
        self.assertIsInstance(fleet, Fleet)
    
    def test_assigned_fleet_matches_name(self):
        fleet_name = 'California'
        driver = Driver('Test', fleet_name)
        fleet = driver.fleet
        self.assertEqual(fleet.name, fleet_name)

class TestAllDrivers(unittest.TestCase):
    def test_driver_file_name_is_str(self):
        pass
    def test_raw_hours_is_dataframe(self):
        pass
