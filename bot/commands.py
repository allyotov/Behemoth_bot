import logging
from datetime import datetime, timedelta
from urllib import response
import pytz 

import httpx
from telegram import ParseMode
from bot import client
#from telegram.ext import ConversationHandler

from bot.client import Subscriber, BehemothClient as Client
# from bot.client import Subscriber
from bot.config import backend_url, prev_days, hello_message
from bot.tools.make_messages import convert_news_to_messages
from bot.tools.initial_datetime import get_current_datetime


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def convert_date_to_str(date_obj):
    return datetime.strftime(date_obj, '%Y-%m-%d-%H-%M-%S-%z')


def hello(update, context):
    try:
        behemoth_client = Client(backend_url)
        subscribers = behemoth_client.get_subscribers()
        if not subscribers:
            logger.debug('Пока нет ни одного подписчика, создаём нового.')
            ids = []
        else:
            ids = [s.id for s in subscribers]
            logger.debug(ids)
        logger.info(subscribers)
        user = update.message.from_user
        logger.debug(user)
        if user['id'] not in ids:
            # save id into backend
            backend_client = Client(backend_url)
            backend_client.send_subscriber(Subscriber(id=user['id'], last_update=(get_current_datetime - timedelta(days=prev_days))))
        # if user_id not in subscribers
        update.message.reply_text(hello_message)
    except Exception as exc:
        logging.exception(exc)
        update.message.reply_text('Что-то пошло не так. Попробуйте отправить /start позже.')
        return


def get_news(context):
    logger.debug('Проверяем новости в бекенде.')
    try:
        behemoth_client = Client(backend_url)
        
        # 1. запрашиваем подписчиков в бекенде
        subscribers = behemoth_client.get_subscribers()
        if not subscribers:
            logger.debug('Нет ни одного подписчика.')
            return
        logger.debug(subscribers)

        # 2. определяем наименьшую дату последнего обновелния среди них
        earliest_last_update = get_earliest_last_update(subscribers)
        logger.debug(earliest_last_update)
        logger.debug(type(earliest_last_update))

        # 3. запрашиваем новости в бекенде начиная с наименьшей даты последнего обновления 
        parameters = {'period': 'from',
                        'date': datetime.strftime(earliest_last_update, '%Y-%m-%d-%H-%M-%S-%z')}
        news = behemoth_client.search_news(**parameters)
        logger.debug(news)
        logger.debug(type(news))
        
        if not news:
            logger.debug('Свежих новостей нет.')
            return

        passed_meetings_msgs, future_meetings_msgs, news_msgs = convert_news_to_messages(news)
        
        present_moment = get_current_datetime()

        for subscriber in subscribers:
            # 1. получаем дату последнего обновления
            last_update = subscriber.last_update
            # 2. обрабатываем новости
            actual_news_msgs = [msg['message'] for msg in news_msgs if msg['update_time'] - last_update > timedelta(seconds=0)]
            if actual_news_msgs:
                context.bot.send_message(chat_id=subscriber.id, text='<b>Свежие новости:</b>', parse_mode=ParseMode.HTML)
                for msg in actual_news_msgs:
                    context.bot.send_message(chat_id=subscriber.id, text=msg, parse_mode=ParseMode.HTML)
            # 3. обрабатываем прошедшие встречи
            actual_passed_meetings_msgs = [msg['message'] for msg in passed_meetings_msgs if msg['update_time'] - last_update > timedelta(seconds=0)]
            if actual_passed_meetings_msgs:
                context.bot.send_message(chat_id=subscriber.id, text='<b>Состоявшиеся встречи:</b>', parse_mode=ParseMode.HTML)
                for msg in actual_passed_meetings_msgs:
                    context.bot.send_message(chat_id=subscriber.id, text=msg, parse_mode=ParseMode.HTML)
            # 4. обрабатываем предстоящие встречи
            actual_future_meetings_msgs = [msg['message'] for msg in future_meetings_msgs if msg['update_time'] - last_update > timedelta(seconds=0)]
            if actual_future_meetings_msgs:
                context.bot.send_message(chat_id=subscriber.id, text='<b>Запланированы встречи:</b>', parse_mode=ParseMode.HTML)
                for msg in actual_future_meetings_msgs:
                    context.bot.send_message(chat_id=subscriber.id, text=msg, parse_mode=ParseMode.HTML)
            # 6. сохраняем новую дату последнего обновления
            subscriber.last_update = present_moment
            behemoth_client.edit_subscriber(subscriber)
            logger.debug('Дата последнего обновления обновлена.')

    except Exception as exc:
        logger.exception(exc)
        msg = 'Ой, у нас что-то пошло не так. Попробуй, пожалуйста, запросить встречи чуть позже.'
        # context.bot.send_message(chat_id=chat_id, text=msg)
        logger.debug(msg)


def get_earliest_last_update(subscribers):
    return min([s.last_update for s in subscribers])


def deactivate_subscriber(update, context):
    logger.debug('Деактивация пользователя запущена!')
