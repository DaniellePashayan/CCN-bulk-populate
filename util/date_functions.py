import calendar
import datetime

import pandas as pd
from loguru import logger
from pandas.tseries.holiday import USFederalHolidayCalendar


def check_if_weekend(date):
    """
    Checks if date is a weekend
    """
    # check if date is a datetime object
    if isinstance(date, datetime.datetime):
        return date.weekday() >= 5
    elif isinstance(date, str):
        return pd.to_datetime(date).weekday() >= 5

def check_if_holiday(date):
    if isinstance(date, str):
        date = pd.to_datetime(date)
        
    custom_holidays = {
    '2023-01-02': 'New Years Day',
    '2023-01-16': 'Martin Luther King Jr. Day',
    '2023-02-20': 'Presidents Day',
    '2023-05-29': 'Memorial Day',
    '2023-07-04': 'Independence Day',
    '2023-09-04': 'Labor Day',
    '2023-11-23': 'Thanksgiving Day',
    '2023-12-25': 'Christmas Day',
    '2024-01-01': 'New Years Day',
    }
    holidays_df = pd.DataFrame(list(custom_holidays.items()), columns=['Date', 'Holiday Name'])
    holidays_df['Date'] = pd.to_datetime(holidays_df['Date'])
    
    # add one day to each holiday
    # files are submitted ON holidays, but never the day after
    holidays_df['Date'] = holidays_df['Date'] + datetime.timedelta(days=1)
    
    holidays = holidays_df['Date'].to_list()    

    return date in holidays

def check_if_EOM(date):
    if isinstance(date, str):
        date = pd.to_datetime(date)
        
    return date.day >= calendar.monthrange(date.year, date.month)[1] - 1

def check_last_business_day_of_month(date):
    if isinstance(date, str):
        date = pd.to_datetime(date)
    # get the first day of the month
    FOM = date.replace(day=1)
    EOM = FOM + pd.offsets.MonthEnd(0)
    # return a list of all the weekdays in the month
    last_weekday = [d for d in pd.date_range(FOM, EOM) if d.weekday() < 5][-1]
    return last_weekday.weekday() == 4 and date == last_weekday
    
def check_if_EOM(date):
    if isinstance(date, str):
        date = pd.to_datetime(date)
    return date.day == calendar.monthrange(date.year, date.month)[1]

def get_next_business_day(today):
    if isinstance(today, str):
        today = pd.to_datetime(today)
    
    tomorrow = today + datetime.timedelta(days=1)

    while check_if_weekend(tomorrow) or check_if_holiday(tomorrow) or check_if_EOM(tomorrow) or check_last_business_day_of_month(tomorrow):
        tomorrow += datetime.timedelta(days=1)
    return tomorrow