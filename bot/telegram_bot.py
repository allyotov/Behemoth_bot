import logging
from telegram import bot

from telegram.ext import CommandHandler, ChatMemberHandler, Updater

from bot import commands, config

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def main():
    behemoth_bot = Updater(config.api_key, use_context=True, request_kwargs=config.proxy)
    bot_dispatcher = behemoth_bot.dispatcher


    behemoth_bot.job_queue.run_repeating(commands.get_news, 5)


    bot_dispatcher.add_handler(CommandHandler('start', commands.hello, pass_job_queue=True))
    bot_dispatcher.add_handler(ChatMemberHandler(commands.deactivate_subscriber, pass_user_data=True, pass_chat_data=True))


    logger.info('Бот стартовал;')

    behemoth_bot.start_polling()
    behemoth_bot.idle()