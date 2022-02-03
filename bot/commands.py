import logging
from datetime import datetime, timedelta
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
    context.user_data['last_news'] = week_ago_datetime()
    context.user_data['last_meeting'] = current_datetime()

    update.message.reply_text(''.join([
        'Привет, дорогой любитель Священного Писания! ',
        'Тебя приветствует бот библейского кружка Бехемот. ',
        'Он поможет тебе не пропускать очередные встречи и ',
        ' знать какие отрывки будут читаться на них.',
    ]))
    context.job_queue.run_repeating(check_updates, 30, context=update.message.chat_id)


def get_news(update, context):
    update.message.reply_text('Здесь будем запрашивать новости.')
    try:
        if update.message.text:
            behemoth_client = Client(backend_url)
            parameters = {'period': 'from',
                          'date': datetime.strftime(context.user_data['last_news'], '%Y-%m-%d-%H-%M-%S-%z')}
            response = behemoth_client.search_news(**parameters)
            logger.debug(response)
            logger.debug(type(response))
            tm_messages, newsitem_datetime = convert_news_to_messages(response)
            logger.info(newsitem_datetime)
            if newsitem_datetime - context.user_data['last_news'] > timedelta(seconds=0):
                context.user_data['last_news'] = newsitem_datetime
            logger.info('---->')
            logger.info(context.user_data['last_news'])
            if not tm_messages:
                update.message.reply_text('Пока в базе данных бота нет ни одной новости.')
            for msg in tm_messages:
                update.message.reply_text(text=msg, parse_mode=ParseMode.HTML)
        else:
            update.message.reply_text(
                'Привет, пользователь! Ты не указал интересующую слово или фразу для поиска!',
            )
    except Exception as exc:
        logging.exception(exc)
        update.message.reply_text(
            'Ой, у нас что-то пошло не так. Попробуй, пожалуйста, запросить встречи чуть позже.',
        )


def get_meetings(update, context):
    update.message.reply_text('Здесь будем запрашивать встречи.')
    try:
        if update.message.text:
            behemoth_client = Client(backend_url)
            parameters = {'period': 'from',
                          'date': datetime.strftime(context.user_data['last_meeting'], '%Y-%m-%d-%H-%M-%S-%z')}
            response = behemoth_client.search_meetings()
            logger.debug(response)
            logger.debug(type(response))
            tm_messages, meeting_datetime = convert_meetings_to_messages(response)
            logger.info(meeting_datetime)
            if meeting_datetime - context.user_data['last_meeting'] > timedelta(days=0):
                context.user_data['last_meeting'] = meeting_datetime
            if not tm_messages:
                update.message.reply_text('Пока в базе данных бота нет ни одной встречи.')
            for msg in tm_messages:
                update.message.reply_text(text=msg, parse_mode=ParseMode.HTML)
        else:
            update.message.reply_text(
                'Привет, пользователь! Ты не указал интересующую слово или фразу для поиска!',
            )
    except Exception as exc:
        logging.exception(exc)
        update.message.reply_text(
            'Ой, у нас что-то пошло не так. Попробуй, пожалуйста, запросить встречи чуть позже.',
        )