#PYTHON
from datetime import datetime, timedelta
import os
from typing import List
#3RD PARTY
import pandas as pd
import win32com.client
#LOCAL
from errors import InvalidWorkTimesError
from driver import Driver, AllDrivers
from work_periods import WorkWeek
from helper_functions import get_previous_sunday
import config

class RawHoursReport:
    def __init__(self, omnitracs_file_name: str, week_start: datetime) -> None:
        self.week_start = week_start
        self.raw_hours_dataframe = self.read_omnitracs_report(omnitracs_file_name)
        self.filter_dataframe_by_input_week_start()

    def filter_dataframe_by_driver(self, driver_code) -> pd.DataFrame:
        """ Returns "driver_hours_dataframe" from the RawHoursReport based on "driver.code" """
        return self.raw_hours_dataframe.loc[self.raw_hours_dataframe['DriverId'] == driver_code]

    def read_omnitracs_report(self, omnitracs_file_name: str) -> pd.DataFrame:
        """ Reads Omnitracs Driver Log Export Report CSV and returns Dataframe """
        return pd.read_csv(omnitracs_file_name, header=1, parse_dates=['StartTime'])
    
    def filter_dataframe_by_input_week_start(self):
        """ Resets dataframe filtered by input week_start """
        week_end = self.week_start + timedelta(days=7)
        mask = (self.raw_hours_dataframe['StartTime'] > self.week_start) & (self.raw_hours_dataframe['StartTime'] < week_end)
        self.raw_hours_dataframe = self.raw_hours_dataframe.loc[mask]

class SingleDriverReport:
    seconds_in_7_hours = 25200 #Time needed for government legal rest break 
    days_in_week = 7
    def __init__(self, driver: Driver, driver_dataframe: pd.DataFrame) -> None:
        self.driver = driver
        self.driver_hours_dataframe = driver_dataframe
        self.remove_midnight_times()
        self.remove_duplicate_activities()
        self.all_times_worked = self.get_times_worked()
        try:
            self.set_start_stop_times(self.all_times_worked)
        except InvalidWorkTimesError as e:
            print(e.message)
    
    def remove_midnight_times(self) -> None:
        """
            Resets driver_hours_dataframe.
            Removes all times with 0hrs, 0min, 0seconds and resets index. Midnight times make it near impossible to calculate time worked.
        """
        self.driver_hours_dataframe = self.driver_hours_dataframe.loc[self.driver_hours_dataframe['StartTime'].dt.time != datetime.today().replace(hour=0, minute=0, second=0, microsecond=0).time()]
        self.driver_hours_dataframe = self.driver_hours_dataframe.reset_index(drop=True)

    def remove_duplicate_activities(self) -> None:
        """
            Resets driver_hours_dataframe.
            Removes rows with duplicate values in the Activity column. This helps remove issues where times worked would sometimes be well over 24 hrs.
         """
        self.driver_hours_dataframe = self.driver_hours_dataframe.loc[self.driver_hours_dataframe['Activity'].shift() != self.driver_hours_dataframe['Activity']].reset_index(drop=True)

    def get_times_worked(self) -> List[datetime]:
        """ Finds relevent times worked from driver_hours_dataframe and sets "start_times" and "stop_times" using "set_start_stop_times. """
        first = True
        times_worked = []
        for index, row in self.driver_hours_dataframe.iterrows():
            if first: #Skip first iteration
                times_worked.append(self.driver_hours_dataframe.iloc[0]['StartTime']) #Add First Time to list
                times_worked.append(self.driver_hours_dataframe.iloc[-1]['StartTime']) #Add Last time to list
                first = False
            else:
                previous_row = self.driver_hours_dataframe.iloc[index - 1]
                current_row = row
                duration = (current_row['StartTime'] - previous_row['StartTime']).total_seconds()
                if duration > self.seconds_in_7_hours and previous_row['Activity'] != 'Driving':
                    times_worked.append(previous_row['StartTime'])
                    times_worked.append(current_row['StartTime'])
                #THIS WORKS BUT THE ABOVE IF STATEMENT IS EASIER TO READ. IT NEEDS MORE TESTING
                # if duration > self.seconds_in_8_hours and (previous_row['Activity'] == 'Off-Duty' or previous_row['Activity'] == 'Sleeper'):
                #     times_worked.append(previous_row['StartTime'])
                #     times_worked.append(current_row['StartTime'])
        times_worked.sort()
        return times_worked

    def set_start_stop_times(self, times_worked: List[datetime]):
        """ Sets start and stop times """
        times_worked.sort()
        if len(times_worked) % 2 == 0: #Check there is even number of times.
            self.start_times = [time for i, time in enumerate(times_worked) if i % 2 == 0] #Every even time is a start time
            self.stop_times = [time for i, time in enumerate(times_worked) if i % 2 != 0] #Every odd time is an end time
        else:
            raise InvalidWorkTimesError(self.driver.code, 'There must be the same amount of start times and stop times')
    

class FinalHoursReport:
    def __init__(self, raw_hours_report: RawHoursReport, all_drivers: AllDrivers) -> None:
        self.week_start = raw_hours_report.week_start
        self.driver_work_weeks = []
        self.raw_hours_report = raw_hours_report
        self.all_drivers = all_drivers

    def set_driver_work_weeks(self) -> None:
        """
            Creates work week for each driver in list and appends to list.
        """
        for driver in self.all_drivers.drivers:
            driver_report = SingleDriverReport(driver, self.raw_hours_report.filter_dataframe_by_driver(driver.code))
            work_week = WorkWeek(driver_report, self.week_start)
            if work_week.total_hours_worked != 0:
                self.driver_work_weeks.append(work_week)

    def create_dataframe_for_csv(self) -> pd.DataFrame:
        """ 
            Returns dataframe.
            Creates dataframe with all information of weeks worked. 
        """
        info = []
        for week in self.driver_work_weeks:
            data = {
                'Week Start': week.week_start,
                'Driver Code': week.driver.code,
                'Fleet': week.driver.fleet.name,
                'Days Worked': week.number_days_worked,
                'Total Hours': week.total_hours_worked,
                'Daily Hours': week.hours_per_day,
                'Total Pay': f'${week.total_pay}.00',
                'Pay Per Day': f'${week.pay_per_day}',
                'Pay Per Hour': f'${week.pay_per_hour}',
            }
            for day in week.days_worked:
                day_name = day.start_time.strftime('%A')
                data[f'{day_name} Start'] = day.start_time
                data[f'{day_name} End'] = day.stop_time
                data[f'{day_name} Hours'] = day.hours_worked
                data[f'{day_name} Pay'] = f'${day.pay}.00'

            data['Personal Conveyance'] = week.personal_conveyance_duration

            info.append(data)

        return pd.DataFrame(info)

    def send_report_email(self, subject: str, message: str, recipients: List[str], attachment: str) -> None:
        """ Sends report via email from local outlook profile. """
        ol = win32com.client.Dispatch('Outlook.Application')

        newmail = ol.CreateItem(0)
        newmail.Subject = subject
        newmail.To = '; '.join(recipients)
        newmail.Body = message

        newmail.Attachments.Add(attachment)

        newmail.Send()

    def generate_hours_report(self, send_email: bool=False, TESTING=False) -> str:
        """ 
            Creates driver work weeks and Saves Report dataframe to csv.
            Returns the location of the new File.
        """
        self.set_driver_work_weeks()
        hours_dataframe = self.create_dataframe_for_csv()
        new_file_name = f'{os.path.dirname(os.getcwd())}/driver_hours_{self.week_start.date()}.csv'
        if TESTING:
            print('Test Completed')
            return
        hours_dataframe.to_csv(new_file_name)
        print(f'\n<<<---Data saved to new CSV at: {new_file_name}--->>>\n')
       
        return new_file_name
