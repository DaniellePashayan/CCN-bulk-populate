import calendar
import datetime

import pandas as pd
from loguru import logger
from pandas.tseries.holiday import USFederalHolidayCalendar


def check_weekend(date):
    # 5 = Saturday, 6 = Sunday
    return date.weekday() > 4

def check_if_holiday(date):
    cal = USFederalHolidayCalendar()
    holidays = cal.holidays(start='2023-01-01', end='2024-12-31').to_pydatetime()
    holidays = [(pd.to_datetime(x) + datetime.timedelta(days=1)) for x in holidays]
    # need to remove juneteenth
    excluded_holidays = [datetime.date(x.year, 6, 19) for x in holidays if x.year == 2023]
    
    holidays = [x for x in holidays if x.date() not in excluded_holidays]
    return date in holidays

def check_if_EOM(date):
    # check if the date is the last day of the month
    last_day_of_month = (date.replace(day=28) + datetime.timedelta(days=4)).replace(day=1) - datetime.timedelta(days=1)
    return last_day_of_month == date

def check_if_within_3_days_of_EOM(date):
    # check if the date is the last day 3 days of the month
    last_day_of_month = (date.replace(day=28) + datetime.timedelta(days=4)).replace(day=1) - datetime.timedelta(days=1)
    
    tomorrow = date + datetime.timedelta(days=1)
    
    is_friday = tomorrow.weekday() == 4

    if is_friday:
        within_3_days = (last_day_of_month - date).days <= 2
        return within_3_days
    else:
        return False
    # print(within_3_days)
    # print(is_thursday)
    return 

def get_next_business_day(today):
    import pandas as pd
    tomorrow = today + datetime.timedelta(days=1) 

    # if tomorrow is a friday and day + 2 or day + 3 is EOM   
    while check_weekend(today) or check_if_holiday(today) or check_if_EOM(today) or check_if_within_3_days_of_EOM(tomorrow):
        tomorrow += datetime.timedelta(days=1)
        tomorrow = pd.to_datetime(tomorrow)
    return tomorrow
