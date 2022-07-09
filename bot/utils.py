from datetime import datetime
import calendar
from typing import Tuple


def get_day_of_month_and_days_in_month() -> Tuple[int, int]:
    now = datetime.now()
    day_of_month: int = now.day
    days_in_current_month = calendar.monthrange(now.year, now.month)[1]
    return day_of_month, days_in_current_month
