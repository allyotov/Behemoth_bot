import logging

# import httpx
# from telegram import ParseMode
# from telegram.ext import ConversationHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def hello(update, context):
    update.message.reply_text(''.join([
        'Привет, дорогой любитель Священного Писания! ',
        'Тебя приветствует бот библейского кружка Бехемот.',
        'Он поможет тебе не пропускать очередные встречи и ',
        ' знать какие отрывки будут читаться на них.',
    ]),
    )