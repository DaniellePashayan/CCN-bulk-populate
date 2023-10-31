import os
import sys
import pandas as pd

# Add the path to the directory containing date_functions to the PYTHONPATH environment variable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'util')))

from date_functions import check_if_weekend, check_if_holiday, check_if_EOM, check_last_business_day_of_month, get_next_business_day

def test_check_if_weekend():
    assert check_if_weekend('2023-10-16') == False
    assert check_if_weekend('2023-10-17') == False
    assert check_if_weekend('2023-10-18') == False
    assert check_if_weekend('2023-10-19') == False
    assert check_if_weekend('2023-10-20') == False
    assert check_if_weekend('2023-10-21') == True
    assert check_if_weekend('2023-10-22') == True

def test_check_if_holiday():
    assert check_if_holiday('2023-11-23') == False
    assert check_if_holiday('2023-11-24') == True
    assert check_if_holiday('2023-06-19') == False
    assert check_if_holiday('2023-06-20') == False
    
def test_check_if_EOM():
    assert check_if_EOM('2023-10-30') == False
    assert check_if_EOM('2023-10-31') == True

def test_check_last_business_day_of_month():
    assert check_last_business_day_of_month('2023-09-29') == True
    assert check_last_business_day_of_month('2023-09-28') == False
    assert check_last_business_day_of_month('2023-10-31') == False # since its not a friday, return False
    
def test_get_next_business_day():
    # check for weekend
    assert get_next_business_day('2023-09-14') == pd.to_datetime('2023-09-15')
    assert get_next_business_day('2023-09-15') == pd.to_datetime('2023-09-18')
    
    # check for holiday
    assert get_next_business_day('2023-11-22') == pd.to_datetime('2023-11-23')
    assert get_next_business_day('2023-11-21') == pd.to_datetime('2023-11-22')
    
    # check for EOM
    assert get_next_business_day('2023-09-29') == pd.to_datetime('2023-10-02')
    
    # check for last business day of month
    assert get_next_business_day('2023-09-28') == pd.to_datetime('2023-10-02')
    
    # check all of the above
    assert get_next_business_day('2023-12-28') == pd.to_datetime('2024-01-01')
    assert get_next_business_day('2023-06-30') == pd.to_datetime('2023-07-03')
    
def test_david_examples():
    assert get_next_business_day('2023-12-29') == pd.to_datetime('2024-01-01')
    assert get_next_business_day('2023-09-28') == pd.to_datetime('2023-10-02')
    assert get_next_business_day('2023-07-28') == pd.to_datetime('2023-08-01')
    assert get_next_business_day('2023-04-28') == pd.to_datetime('2023-05-01')
    