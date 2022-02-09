import logging
from datetime import datetime, timedelta

from bot.tools.schemes import NewsItem
from bot.tools.initial_datetime import current_datetime, week_ago_datetime

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
    '0': 'понедельник',
    '1': 'вторник',
    '2': 'среда',
    '3': 'четверг',
    '4': 'пятница',
    '5': 'суббота',
    '6': 'воскресенье'
}


MEETINGS_MESSAGE_TEMPLATE = """<b><strong>{0}</strong></b>
{1} {2} {3}
{4}
{5}
{6}

Изучаемый отрывок: <b><strong>{7}</strong></b>;

{8}
"""

NEWS_MESSAGE_TEMPLATE = """<b><strong>{0}</strong></b>

{1}

{2} {3} {4} {5}
"""

DATETIME_TEMPLATE = '%Y-%m-%dT%H:%M:%S%z'


def convert_news_to_messages(response: list[dict]) -> list[str]:
    tm_messages = []
    last_datetime = week_ago_datetime()
    for result_num, news_str in enumerate(response, start=1):
        newsitem = NewsItem(**news_str)

        newsitem_datetime = datetime.strptime(newsitem.time_created, DATETIME_TEMPLATE)
        if newsitem_datetime - last_datetime > timedelta(days=0):
            last_datetime = newsitem_datetime

        msg = NEWS_MESSAGE_TEMPLATE.format(
            newsitem.title,
            newsitem.text,
            datetime.strftime(newsitem_datetime, '%d'),
            MONTHS[datetime.strftime(newsitem_datetime, '%m')],
            datetime.strftime(newsitem_datetime, '%Y'),
            datetime.strftime(newsitem_datetime, '%H:%M'),
        )
        tm_messages.append(msg)
    return tm_messages, last_datetime
