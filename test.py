from util.date_functions import get_next_business_day as get_next_business_day, check_if_within_3_days_of_EOM
import datetime
from datetime import datetime, timedelta

today = datetime.today()
test = today + timedelta(days=97)
# print(test)

# check_if_within_3_days_of_EOM(test)
print(test)

nbd = get_next_business_day(test)
print(nbd)