from calendar import week
from datetime import datetime, timedelta
import logging
import pytz


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def get_week_ago_datetime():
    return get_localized_datetime(timedelta(days=7))


def get_current_datetime():
    return get_localized_datetime(timedelta(days=0))


def get_localized_datetime(given_timedelta):
    timezone = pytz.timezone('Europe/Moscow')
    needed_date = datetime.now(timezone) - given_timedelta
    logger.debug('NAIVE DATE: %s' % needed_date)
    return needed_date


