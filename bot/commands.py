from calendar import week
import logging
from datetime import datetime, timedelta
from typing import Tuple

from telegram import ParseMode
import telegram


from bot.client import Subscriber, BehemothClient as Client
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
        need_to_send_news = False
        if user['id'] not in ids:
            behemoth_client.send_subscriber(Subscriber(id=user['id'], last_update=(get_current_datetime() - timedelta(days=prev_days))))
            need_to_send_news = True
            update.message.reply_text(hello_message)
        else:
            subscriber = behemoth_client.get_subscribers(**{'id': user['id']})[0]
            if not subscriber.active:
                subscriber.active = True
                behemoth_client.edit_subscriber(subscriber)
                update.message.reply_text('C возвращением! Теперь мы снова будем присылать вам новости и оповещения о запланированных встречах.')
                subscriber, week_more = set_subscriber_last_update_after_comeback(subscriber)
                need_to_send_news = True
        update.message.reply_text('/mute - приостановка рассылки;\n/next - напомнить 2 следующие встречи;\n/prev - напомнить 2 предыдущие встречи.')
        if need_to_send_news:
            title_message='За последнюю неделю'
            no_news_message='За последнюю неделю не было новостей'
            if not week_more:
                title_message='Пока вас не было'
                no_news_message='Пока вас не было, новостей не приходило.'
            send_updates_to_subscribers(subscribers=[subscriber], 
                                        b_client=behemoth_client, 
                                        bot=context.bot, 
                                        title_message=title_message,
                                        no_news_message=no_news_message)
            send_updates_to_subscribers(subscribers=[subscriber], b_client=behemoth_client, bot=context.bot)

        
    except Exception as exc:
        logger.exception(exc)
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
        for subscriber in subscribers:
            try:
                logger.debug(context.bot.get_chat_member(subscriber.id, subscriber.id))
                context.bot.sendChatAction(chat_id=subscriber.id, action=telegram.ChatAction.TYPING)
                logger.debug('TYPING успешно отправлено.')
            except Exception as exc:
                logger.debug('что-то не так с пользователем')
                logger.exception(exc)
        
        send_updates_to_subscribers(subscribers=subscribers, b_client=behemoth_client, bot=context.bot)

    except Exception as exc:
        logger.exception(exc)
        msg = 'Ой, у нас что-то пошло не так. Попробуй, пожалуйста, запросить встречи чуть позже.'
        # context.bot.send_message(chat_id=chat_id, text=msg)
        logger.debug(msg)


def get_earliest_last_update(subscribers):
    return min([s.last_update for s in subscribers])


def deactivate_subscriber(update, context):
    logger.debug('Деактивация пользователя запущена!')

def mute(update, context):
    try:
        behemoth_client = Client(backend_url)
        subscribers = behemoth_client.get_subscribers(**{'id': update.message.chat.id})
        logger.debug(subscribers)
        if not subscribers:
            logger.debug(update.message.chat.id)
            logger.debug('Почему-то нет такого подписчика в базе.')
        subscriber = subscribers[0]
        logger.debug('\n\n\n\n\n\n\n\n\n')
        logger.debug(subscriber.active)
        if subscriber.active:
            subscriber.active = False
            logger.debug(subscriber.active)
            behemoth_client.edit_subscriber(subscriber)
            update.message.reply_text('Теперь оповещения для вас отключены. Чтобы включить их снова, повторно отправьте боту команду /mute')
        else:
            subscriber.active = True
            behemoth_client.edit_subscriber(subscriber)
            update.message.reply_text('C возвращением! Теперь мы снова будем присылать вам новости и оповещения о запланированных встречах.')
            subscriber, week_more = set_subscriber_last_update_after_comeback(subscriber)
            if week_more:
                title_message='За последнюю неделю'
                no_news_message='За последнюю неделю не было новостей'
            else:
                title_message='Пока вас не было'
                no_news_message='Пока вас не было, новостей не приходило.'
            send_updates_to_subscribers(subscribers=[subscriber], 
                                        b_client=behemoth_client, 
                                        bot=context.bot, 
                                        title_message=title_message,
                                        no_news_message=no_news_message)

    except Exception as exc:
        logger.exception(exc)
        update.message.reply_text('Что-то пошло не так. Попробуйте отправить /mute позже.')
        return


def send_updates_to_subscribers(subscribers, b_client, bot, title_message=None, no_news_message=None):
    # 2. определяем наименьшую дату последнего обновелния среди них
    earliest_last_update = get_earliest_last_update(subscribers)
    logger.debug(earliest_last_update)
    logger.debug(type(earliest_last_update))

    # 3. запрашиваем новости в бекенде начиная с наименьшей даты последнего обновления 
    parameters = {'period': 'from',
                    'date': datetime.strftime(earliest_last_update, '%Y-%m-%d-%H-%M-%S-%z')}
    news = b_client.search_news(**parameters)
    logger.debug(news)
    logger.debug(type(news))
    
    if not news:
        logger.debug('Свежих новостей нет.')
        
        if title_message:
            for subscriber in subscribers:
                bot.send_message(chat_id=subscriber.id, text=no_news_message)
        return


    passed_meetings_msgs, future_meetings_msgs, news_msgs = convert_news_to_messages(news)
    
    present_moment = get_current_datetime()

    for subscriber in subscribers:
        if title_message:
            bot.send_message(chat_id=subscriber.id, text=title_message)
        # 1. получаем дату последнего обновления
        last_update = subscriber.last_update
        # 2. обрабатываем новости
        actual_news_msgs = [msg['message'] for msg in news_msgs if msg['update_time'] - last_update > timedelta(seconds=0)]
        if actual_news_msgs:
            bot.send_message(chat_id=subscriber.id, text='<b>Свежие новости:</b>', parse_mode=ParseMode.HTML)
            for msg in actual_news_msgs:
                bot.send_message(chat_id=subscriber.id, text=msg, parse_mode=ParseMode.HTML)
        # 3. обрабатываем прошедшие встречи
        actual_passed_meetings_msgs = [msg['message'] for msg in passed_meetings_msgs if msg['update_time'] - last_update > timedelta(seconds=0)]
        if actual_passed_meetings_msgs:
            bot.send_message(chat_id=subscriber.id, text='<b>Состоявшиеся встречи:</b>', parse_mode=ParseMode.HTML)
            for msg in actual_passed_meetings_msgs:
                bot.send_message(chat_id=subscriber.id, text=msg, parse_mode=ParseMode.HTML)
        # 4. обрабатываем предстоящие встречи
        actual_future_meetings_msgs = [msg['message'] for msg in future_meetings_msgs if msg['update_time'] - last_update > timedelta(seconds=0)]
        if actual_future_meetings_msgs:
            bot.send_message(chat_id=subscriber.id, text='<b>Запланированы встречи:</b>', parse_mode=ParseMode.HTML)
            for msg in actual_future_meetings_msgs:
                bot.send_message(chat_id=subscriber.id, text=msg, parse_mode=ParseMode.HTML)
        # 6. сохраняем новую дату последнего обновления
        subscriber.last_update = present_moment
        b_client.edit_subscriber(subscriber)
        logger.debug('Дата последнего обновления обновлена.')

    
def set_subscriber_last_update_after_comeback(subscriber: Subscriber) -> Tuple[Subscriber, bool]:
    week_more = False
    if get_current_datetime() - subscriber.last_update > timedelta(days=8):
        week_more = True
        subscriber.last_update = (get_current_datetime() - timedelta(days=prev_days))
    return subscriber, week_more