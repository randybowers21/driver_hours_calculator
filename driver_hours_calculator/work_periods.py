#PYTHON
from datetime import datetime, timedelta
from typing import TYPE_CHECKING
#PIP
#LOCAL
from driver_hours_calculator.helper_functions import get_previous_sunday

if TYPE_CHECKING:
    from report import SingleDriverReport

class WorkWeek:
    days_in_week = 7
    def __init__(self, driver_report: 'SingleDriverReport', week_start: datetime=get_previous_sunday(1)): #Quotes around SingleDriverReport are for type checking import
        self.week_start = week_start
        self.driver_report = driver_report
        self.driver = driver_report.driver
        self.days_worked = []
        self.create_work_days()
        self.create_empty_work_days()
        self.sort_days_worked_by_start_time()
        self.calculate_totals()
        
    def create_work_days(self):
        """
            Loops through start times to make sure they are within a week from week_start
        """
        for i, start_time in enumerate(self.driver_report.start_times):
            if start_time > self.week_start + timedelta(weeks=1):
                continue
            else:
                stop_time = self.driver_report.stop_times[i]
                work_day = WorkDay(self.driver.fleet, start_time, stop_time)

            self.days_worked.append(work_day)
    
    def create_empty_work_days(self):
        dates_worked = [date.date() for date in self.driver_report.start_times]
        for day_num in range(self.days_in_week):
            day = self.week_start + timedelta(day_num)
            if day.date() not in dates_worked:
                self.days_worked.append(WorkDay(self.driver.fleet, start_time=day, stop_time=day))
            
    def calculate_totals(self):
        #Personal Conveyance info
        pc_duration_in_seconds = self.driver_report.driver_hours_dataframe.loc[self.driver_report.driver_hours_dataframe['Activity'] == 'Personal Conv.']['Duration'].sum()
        self.personal_conveyance_duration = round(pc_duration_in_seconds / 60, 2)
        #Total Hours info
        self.total_hours_worked = round(sum(day.hours_worked for day in self.days_worked), 2)

        try:
            self.total_pay = round(sum(day.pay for day in self.days_worked), 2)
        except TypeError as e:
            print(e)
            print(self.driver.code)
            print(self.days_worked)
        self.number_days_worked = round(len([day.hours_worked for day in self.days_worked if day.hours_worked > 0]), 2)
        if self.number_days_worked == 0 or self.total_hours_worked == 0:
            self.hours_per_day = 0
            self.pay_per_day = 0
            self.pay_per_hour = 0
        else:
            self.hours_per_day = round(self.total_hours_worked / self.number_days_worked, 2)
            self.pay_per_day = round(self.total_pay / self.number_days_worked, 2)
            self.pay_per_hour = round(self.total_pay / self.total_hours_worked, 2)

    def sort_days_worked_by_start_time(self):
        self.days_worked.sort(key=lambda x: x.start_time)

    def __repr__(self) -> str:
        return (
            f'Driver: {self.driver.code}\n'
            f'Week: {self.week_start.date()} to {(self.week_start + timedelta(weeks=1)).date()}\n'
            f'Fleet: {self.driver.fleet.name}\n'
            f'Days Worked: {self.number_days_worked} '
            f'Hours Worked: {self.total_hours}\n'
            f'Hours Per Day: {self.hours_per_day}\n'
            f'Total Pay: {self.total_pay} '
            f'Daily Pay: {self.pay_per_day} '
            f'Hourly Pay: {self.pay_per_hour} ' 
    )

class WorkDay:
    seconds_in_hour = 3600
    def __init__(self, fleet, start_time, stop_time):
        self.start_time = start_time
        self.stop_time = stop_time
        self.fleet = fleet
        self.calculate_info()
    
    def calculate_info(self):
        self.hours_worked = round((self.stop_time - self.start_time).total_seconds() / self.seconds_in_hour, 2)
        self.pay = self.calculate_pay(self.hours_worked)

    def calculate_pay(self, hours: int):
        for ring in self.fleet.rings:
            if hours == 0 or hours > 24:
                return round(0, 2)
            elif hours <= ring.high_hours:
                return round(ring.pay, 2)
    
    def __repr__(self):
        return (
            f'Start: {self.start_time} '
            f'End: {self.stop_time}\n'
            f'Hours Worked: {self.hours_worked} '
            f'Pay: {self.pay}'
        )