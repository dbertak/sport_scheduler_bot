from telegram.ext import Updater, CommandHandler

from handlers import start, show_help
from config import CONFIG

import logging


logging.basicConfig(format=CONFIG['logging']['format'], level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    updater = Updater(token=CONFIG['bot_token'], use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('help', show_help))
    # possibly other commands lol


    logger.info('Bot started')
    updater.start_polling()

    updater.idle()

if __name__ == '__main__':
    main()
