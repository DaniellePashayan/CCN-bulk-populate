import datetime
import calendar
from pandas.tseries.holiday import USFederalHolidayCalendar

def check_weekend(curr_date):
    # 5 = Saturday, 6 = Sunday
    return curr_date.weekday() > 4

def check_if_holiday(curr_date):
    cal = USFederalHolidayCalendar()
    holidays = cal.holidays(start='2023-01-01', end='2024-12-31').to_pydatetime()
    holidays = [(x.date() + datetime.timedelta(days=1)) for x in holidays]
    # need to remove juneteenth
    holidays = [x for x in holidays if x != datetime.date(x.year, 6, 20)]
    return curr_date in holidays

def check_if_EOM(curr_date):
    # check if the date is the last day of the month
    last_day_of_month = (curr_date.replace(day=28) + datetime.timedelta(days=4)).replace(day=1) - datetime.timedelta(days=1)
    return last_day_of_month == curr_date

def get_next_business_day(tomorrow):
    while check_weekend(tomorrow) or check_if_holiday(tomorrow) or check_if_EOM(tomorrow):
        tomorrow += datetime.timedelta(days=1)
    return tomorrow