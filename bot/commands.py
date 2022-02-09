import logging
from datetime import datetime, timedelta
from urllib import response
import pytz 

import httpx
from telegram import ParseMode
#from telegram.ext import ConversationHandler

from bot.client import Subscriber, BehemothClient as Client
# from bot.client import Subscriber
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
        backend_client = Client(backend_url)
        backend_client.send_subscriber(Subscriber(id=user['id'], last_update=(datetime.now())))
    # if user_id not in subscribers
    update.message.reply_text(hello_message)


def get_news(context):
    logger.debug('Проверяем новости в бекенде.')
    try:
        behemoth_client = Client(backend_url)
        subscribers = behemoth_client.get_subscribers()
        logger.debug(subscribers)
        earliest_last_update = get_earliest_last_update(subscribers)
        logger.debug(earliest_last_update)
        logger.debug(type(earliest_last_update))
        parameters = {'period': 'from',
                        'date': datetime.strftime(earliest_last_update, '%Y-%m-%d-%H-%M-%S-%z')}
        response = behemoth_client.search_news(**parameters)
        logger.debug(response)
        logger.debug(type(response))
        
        # tm_messages, newsitem_datetime = convert_news_to_messages(response)
        # logger.info(newsitem_datetime)

        # for subscriber in subscribers:
        #     subscriber.id
        #     if tm_messages:
        #         context.bot.send_message(chat_id=chat_id, text='Свежие новости:')
        #     for msg in tm_messages:
        #         context.bot.send_message(chat_id=chat_id, text=msg, parse_mode=ParseMode.HTML)
        



        # if newsitem_datetime - user_data['last_news'] > timedelta(seconds=0):
        #     user_data['last_news'] = newsitem_datetime
        # logger.info('---->')
        # logger.info(user_data['last_news'])


    except Exception as exc:
        logging.exception(exc)
        msg = 'Ой, у нас что-то пошло не так. Попробуй, пожалуйста, запросить встречи чуть позже.'
        # context.bot.send_message(chat_id=chat_id, text=msg)
        logger.debug(msg)

def get_earliest_last_update(subscribers):
    return min([s.last_update for s in subscribers])

def get_subscriber_list_from_backend():
    try:
        behemoth_client = Client(backend_url)
        response = behemoth_client.get_subscribers()
        logger.debug(response)
        return response
    except Exception as exc:
        logging.exception(exc)
