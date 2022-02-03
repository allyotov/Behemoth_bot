import logging

from telegram.ext import CommandHandler, Updater

from bot import commands, config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    behemoth_bot = Updater(config.api_key, use_context=True, request_kwargs=config.proxy)

    bot_dispatcher = behemoth_bot.dispatcher

    #bot_dispatcher.job_queue.run_repeating(commands.check_updates, interval=3, first=0, name='update_cheking', context=behemoth_bot)

    bot_dispatcher.add_handler(CommandHandler('start', commands.hello, pass_job_queue=True))

    logger.info('Бот стартовал;')

    behemoth_bot.start_polling()

    behemoth_bot.idle()