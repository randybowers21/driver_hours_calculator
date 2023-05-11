# PYTHON

# PIP
# LOCAL
import driver_hours_calculator.gui as gui

def app():
    user_interface = gui.UserInterface()
    user_interface.mainloop()

if __name__ == "__main__":
    app()


#USED FOR MASS CREATION OF REPORTS
# from datetime import datetime, timedelta
# import pandas as pd
# import driver_hours_calculator.report as report
# import driver_hours_calculator.drivers as drivers
# from driver_hours_calculator.helper_functions import get_previous_sunday
# import driver_hours_calculator.config as config

# def create_final_hours_report(file_name, start_date):
#     raw_hours_report = report.RawHoursReport(file_name, week_start=start_date)
#     all_drivers = drivers.AllDrivers(raw_hours_report.raw_hours_dataframe)
#     final_report = report.FinalHoursReport(raw_hours_report=raw_hours_report, all_drivers=all_drivers)
#     return final_report.generate_hours_report(SAVE_FILE=True)

# def create_all_reports():
#     items = []
#     start_date = datetime(2023,1,1)
#     while start_date <= datetime(2023, 4, 23):
#         items.append(create_final_hours_report('DriverLogExport(1).csv', start_date))
#         start_date += timedelta(days=7)
#     pd.concat(items).to_csv('TEST HOURS.csv')
    
# df = create_final_hours_report('DriverLogExport.csv', datetime(2023, 4, 30))
