#PYTHON
from typing import List
#3RD PARTY
import pandas as pd
#LOCAL
from driver_hours_calculator.fleets import FleetFactory

class AllDrivers:
    def __init__(self, raw_hours_dataframe: pd.DataFrame, master_driver_file_location: str ='X:\Driver Hours\Master File.xlsx') -> None:
        self.raw_hours_dataframe = raw_hours_dataframe
        self.master_driver_file = master_driver_file_location
        self.master_driver_list_sheet_name = 'Drivers'
        self.drivers = None
        self.create_drivers()

    @property
    def all_driver_codes(self):
        return self.raw_hours_dataframe['DriverId'].unique()
    
    @all_driver_codes.setter
    def all_driver_codes(self, all_driver_codes: List[str]):
        self.all_driver_codes = all_driver_codes

    @property
    def daily_wage_driver_info(self):
        return pd.read_excel(self.master_driver_file, sheet_name=self.master_driver_list_sheet_name)

    @daily_wage_driver_info.setter
    def daily_wage_driver_info(self, daily_wage_driver_info):
        self.daily_wage_driver_info = daily_wage_driver_info

    def create_drivers(self):
        """ Creates a Driver instance for each driver code in list and adds to list """
        self.drivers = []
        daily_wage_driver_codes = list(self.daily_wage_driver_info['Driver Code'])
        daily_wage_fleets = list(self.daily_wage_driver_info['Fleet'])

        #NEW WAY takes .5 ish seconds to run
        for driver_code in self.all_driver_codes:
            if driver_code not in daily_wage_driver_codes:
                fleet_name = 'Cent Per Mile'

            else:
                index = daily_wage_driver_codes.index(driver_code)
                fleet_name = daily_wage_fleets[index]
            
            self.drivers.append(Driver(driver_code, fleet_name))
        #OLD WAY FOR POSTERITYS SAKE TOOK 4.9 ish seconds to run.
        # for driver_code in self.all_driver_codes:
        #     if driver_code not in daily_wage_driver_codes:
        #         fleet_name = 'Cent Per Mile'
        #         Driver(driver_code, fleet_name)
        #     else:
        #         fleet_name = self.daily_wage_driver_info.loc[self.daily_wage_driver_info['Driver Code'] ==  driver_code].values[0]
        #         Driver(driver_code, fleet_name)

class Driver:
    def __init__(self, driver_code: str, fleet_name: str) -> None:
         self.code = driver_code
         self.fleet_name = fleet_name
         self.assign_fleet()

    def assign_fleet(self):
        self.fleet = FleetFactory().get_fleet(self.fleet_name)
