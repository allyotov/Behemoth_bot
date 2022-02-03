import logging

# import httpx
# from telegram import ParseMode
# from telegram.ext import ConversationHandler


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_updates(context):
    logger.debug(context)
    context.bot.send_message(chat_id=context.job.context, text='Здесь будет периодическая проверка новостей и встреч')

def hello(update, context):
    update.message.reply_text(''.join([
        'Привет, дорогой любитель Священного Писания! ',
        'Тебя приветствует бот библейского кружка Бехемот. ',
        'Он поможет тебе не пропускать очередные встречи и ',
        ' знать какие отрывки будут читаться на них.',
    ]))
    context.job_queue.run_repeating(check_updates, 30, context=update.message.chat_id)
