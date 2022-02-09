import logging
from datetime import datetime, timedelta
from urllib import response
import pytz 

import httpx
from telegram import ParseMode
#from telegram.ext import ConversationHandler

from bot.client.client import BehemothClient as Client
from bot.config import backend_url
from bot.tools.json_telegram import convert_meetings_to_messages, convert_news_to_messages
from bot.tools.initial_datetime import current_datetime, week_ago_datetime


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def convert_date_to_str(date_obj):
    return datetime.strftime(date_obj, '%Y-%m-%d-%H-%M-%S-%z')


def check_updates(context):
    logger.debug(context)
    context.bot.send_message(chat_id=context.job.context, text='Здесь будет периодическая проверка новостей и встреч')


def hello(update, context):
    user = update.message.from_user
    print('You talk with user {} and his user ID: {} '.format(user['username'], user['id']))
    return
    if 'last_news' not in context.user_data:
        context.user_data['last_news'] = week_ago_datetime()
    if 'last_meeting' not in context.user_data:
        context.user_data['last_meeting'] = current_datetime()

    update.message.reply_text(''.join([
        'Привет, дорогой любитель Священного Писания! ',
        'Тебя приветствует бот библейского кружка Бехемот. ',
        'Он поможет тебе не пропускать очередные встречи и ',
        ' знать какие отрывки будут читаться на них.',
    ]))
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
        response.raise_for_status()
        logger.debug(response)
        return response
    except Exception as exc:
        logging.exception(exc)
