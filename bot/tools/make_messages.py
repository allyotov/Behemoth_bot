import logging
from typing import Tuple
from datetime import datetime, timedelta, timezone

from bot.client import NewsItem
from bot.tools.initial_datetime import get_current_datetime

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


MONTHS = {
    '01': 'января',
    '02': 'февраля',
    '03': 'марта',
    '04': 'апреля',
    '05': 'мая',
    '06': 'июня',
    '07': 'июля',
    '08': 'августа',
    '09': 'сентября',
    '10': 'октября',
    '11': 'ноября',
    '12': 'декабря'
}

WEEKDAYS = {
    0: 'в понедельник',
    1: 'во вторник',
    2: 'в среду',
    3: 'в четверг',
    4: 'в пятницу',
    5: 'в субботу',
    6: 'в воскресенье'
}


MEETINGS_MESSAGE_TEMPLATE = """<b><strong>Встреча {0}</strong></b>
<b><strong>{1} {2} {3} {4}</strong></b>
{5}

Отредактирована: {6} {7} {8} в {9}
"""

NEWS_MESSAGE_TEMPLATE = """{0} {1} {2} {3} 
{4}
"""

DATETIME_TEMPLATE = '%Y-%m-%dT%H:%M:%S%z'


def convert_news_to_messages(news: list[NewsItem]) -> Tuple[list[dict], list[dict], list[dict]]:
    passed_meetings_msgs = []
    future_meetings_msgs = []
    news_msgs = []

    for newsitem in news:
        if newsitem.meeting_time is None:
            msg = NEWS_MESSAGE_TEMPLATE.format(
                    datetime.strftime(newsitem.updated_time, '%d'),
                    MONTHS[datetime.strftime(newsitem.updated_time, '%m')],
                    datetime.strftime(newsitem.updated_time, '%Y'),
                    datetime.strftime(newsitem.updated_time, '%H:%M'),
                    newsitem.text
                )
            news_msgs.append({'message': msg, 'update_time': newsitem.updated_time})
        else:
            msg = MEETINGS_MESSAGE_TEMPLATE.format(
                    WEEKDAYS[newsitem.meeting_time.weekday()],
                    datetime.strftime(newsitem.meeting_time, '%d'),
                    MONTHS[datetime.strftime(newsitem.meeting_time, '%m')],
                    datetime.strftime(newsitem.meeting_time, '%Y'),
                    datetime.strftime(newsitem.meeting_time, '%H:%M'),
                    newsitem.text,
                    datetime.strftime(newsitem.updated_time, '%d'),
                    MONTHS[datetime.strftime(newsitem.updated_time, '%m')],
                    datetime.strftime(newsitem.updated_time, '%Y'),
                    datetime.strftime(newsitem.updated_time, '%H:%M'),
            )
            if get_current_datetime() - newsitem.meeting_time > timedelta(seconds=0):
                passed_meetings_msgs.append({'message': msg, 'update_time': newsitem.updated_time})
            else:
                future_meetings_msgs.append({'message': msg, 'update_time': newsitem.updated_time})

    return passed_meetings_msgs, future_meetings_msgs, news_msgs
