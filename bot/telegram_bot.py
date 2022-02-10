import logging
from telegram import bot

from telegram.ext import CommandHandler, ChatMemberHandler, Updater

from bot import commands, config

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def main():
    behemoth_bot = Updater(config.api_key, use_context=True, request_kwargs=config.proxy)
    bot_dispatcher = behemoth_bot.dispatcher

    bot_dispatcher.add_handler(ChatMemberHandler(commands.deactivate_user))

    behemoth_bot.job_queue.run_repeating(commands.get_news, 5)


    bot_dispatcher.add_handler(CommandHandler('start', commands.hello))
    bot_dispatcher.add_handler(CommandHandler('mute', commands.mute))
    bot_dispatcher.add_handler(CommandHandler('next', commands.get_next_meetings))
    bot_dispatcher.add_handler(CommandHandler('prev', commands.get_prev_meetings))


    logger.info('Бот стартовал;')

    behemoth_bot.start_polling()
    behemoth_bot.idle()