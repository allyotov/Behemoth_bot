import logging
from datetime import datetime, timedelta
from urllib import response
import pytz 

import httpx
from telegram import ParseMode
#from telegram.ext import ConversationHandler

from bot.client import BehemothClient as Client
from bot.client import Subscriber
from bot.config import backend_url, prev_days, hello_message
from bot.tools.json_telegram import convert_news_to_messages
from bot.tools.initial_datetime import current_datetime, week_ago_datetime


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def convert_date_to_str(date_obj):
    return datetime.strftime(date_obj, '%Y-%m-%d-%H-%M-%S-%z')


def check_updates(context):
    logger.debug(context)
    context.bot.send_message(chat_id=context.job.context, text='Здесь будет периодическая проверка новостей и встреч')


def hello(update, context):
    subscribers = get_subscriber_list_from_backend()
    if subscribers:
        pass
    else:
        ids = subscribers
    logger.info(subscribers)
    user = update.message.from_user
    if user['id'] not in ids:
        # save id into backend
        Client.send_subscriber(id=id, last_update=(datetime.now() - timedelta(days=prev_days)))
    # if user_id not in subscribers
    update.message.reply_text(hello_message)
    return
    if 'last_news' not in context.user_data:
        context.user_data['last_news'] = week_ago_datetime()
    if 'last_meeting' not in context.user_data:
        context.user_data['last_meeting'] = current_datetime()

 
    context.job_queue.run_repeating(get_news, 5, context=(update.message.chat_id, context.user_data))
    context.job_queue.run_repeating(get_meetings, 5, context=(update.message.chat_id, context.user_data))


def get_news(context):
    chat_id, user_data = context.job.context
    try:
        behemoth_client = Client(backend_url)
        parameters = {'period': 'from',
                        'date': datetime.strftime(user_data['last_news'], '%Y-%m-%d-%H-%M-%S-%z')}
        response = behemoth_client.search_news(**parameters)
        logger.debug(response)
        logger.debug(type(response))
        tm_messages, newsitem_datetime = convert_news_to_messages(response)
        logger.info(newsitem_datetime)
        if newsitem_datetime - user_data['last_news'] > timedelta(seconds=0):
            user_data['last_news'] = newsitem_datetime
        logger.info('---->')
        logger.info(user_data['last_news'])
        if tm_messages:
            context.bot.send_message(chat_id=chat_id, text='Свежие новости:')
        for msg in tm_messages:
            context.bot.send_message(chat_id=chat_id, text=msg, parse_mode=ParseMode.HTML)

    except Exception as exc:
        logging.exception(exc)
        msg = 'Ой, у нас что-то пошло не так. Попробуй, пожалуйста, запросить встречи чуть позже.'
        context.bot.send_message(chat_id=chat_id, text=msg)


def get_subscriber_list_from_backend():
    try:
        behemoth_client = Client(backend_url)
        response = behemoth_client.get_subscribers()
        logger.debug(response)
        return response
    except Exception as exc:
        logging.exception(exc)


def convert_subscriber(subscriber, id: int, last_update: datetime) -> Subscriber:
    return Subscriber(id=id, last_update=last_update)