import logging
from datetime import datetime, timedelta

from bot.tools.schemes import Meeting, NewsItem
from bot.tools.initial_datetime import current_datetime, week_ago_datetime

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


MEETINGS_MESSAGE_TEMPLATE = """<b><strong>{0}</strong></b>

Изучаемый отрывок: <b><strong>{1}</strong></b>;

{2}

Время проведения: {3};
Будет проводится: {4}."""

NEWS_MESSAGE_TEMPLATE = """<b><strong>{0}</strong></b>

{1}

Время cоздания: {2};
(Внёс в базу бота: {3}.)"""

DATETIME_TEMPLATE = '%Y-%m-%dT%H:%M:%S%z'


def convert_meetings_to_messages(response: list[dict]) -> list[str]:
    tm_messages = []
    last_datetime = datetime.strptime(response[0]['time'], DATETIME_TEMPLATE)
    for result_num, meeting_str in enumerate(response, start=1):
        meeting = Meeting(**meeting_str)
        if meeting.intramural == '0':
            meeting.intramural = 'В Zoom'
        else:
            meeting.intramural = 'Очно'

        meeting_datetime = datetime.strptime(meeting.time, DATETIME_TEMPLATE)

        if meeting_datetime - last_datetime > timedelta(days=0):
            last_datetime = meeting_datetime

        msg = MEETINGS_MESSAGE_TEMPLATE.format(
            meeting.name,
            meeting.fragment,
            meeting.comment,
            meeting.time,
            meeting.intramural,
        )
        tm_messages.append(msg)
    return tm_messages, last_datetime


def convert_news_to_messages(response: list[dict]) -> list[str]:
    tm_messages = []
    last_datetime = datetime.strptime(response[0]['time_created'], DATETIME_TEMPLATE)
    for result_num, news_str in enumerate(response, start=1):
        newsitem = NewsItem(**news_str)

        newsitem_datetime = datetime.strptime(newsitem.time_created, DATETIME_TEMPLATE)
        if newsitem_datetime - last_datetime > timedelta(days=0):
            last_datetime = newsitem_datetime

        msg = NEWS_MESSAGE_TEMPLATE.format(
            newsitem.title,
            newsitem.text,
            newsitem.time_created,
            newsitem.author,
        )
        tm_messages.append(msg)
    return tm_messages, last_datetime



'''
class Meeting(BaseModel):
    name: str
    fragment: str
    comment: str
    time: str
    intramural: int


class NewsItem(BaseModel):
    title: str
    text: str
    time_created: str
    author: str

'''