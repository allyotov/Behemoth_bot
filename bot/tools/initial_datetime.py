from datetime import datetime, timedelta
import pytz


def get_week_ago_datetime():
    return get_localized_datetime(timedelta(days=7))


def get_current_datetime():
    return get_localized_datetime(timedelta(days=0))


def get_localized_datetime(given_timedelta):
    naive = datetime.now() - given_timedelta
    # timezone = pytz.utc
    timezone = pytz.timezone('Europe/Moscow')
    week_ago_date = timezone.localize(naive)
    return week_ago_date


