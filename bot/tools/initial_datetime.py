from calendar import week
from datetime import datetime, timedelta
from time import time
import pytz


def week_ago_datetime():
    return localized_datetime(timedelta(days=7))


def current_datetime():
    return localized_datetime(timedelta(days=0))


def localized_datetime(given_timedelta):
    naive = datetime.now() - given_timedelta
    timezone = pytz.timezone('Europe/Moscow')
    week_ago_date = timezone.localize(naive)
    return week_ago_date


