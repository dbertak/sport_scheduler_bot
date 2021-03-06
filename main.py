from telegram.ext import Updater, CommandHandler

from config import CONFIG
from handlers import *

import logging


logging.basicConfig(format=CONFIG['logging']['format'], level=CONFIG['logging']['level'])
logger = logging.getLogger(__name__)


def main():
    updater = Updater(token=CONFIG['bot_token'], use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('help', show_help))
    dispatcher.add_handler(CommandHandler('showsports', show_sports))
    dispatcher.add_handler(CommandHandler('newmatch', new_match))
    dispatcher.add_handler(CommandHandler('matchinfo', get_info))
    dispatcher.add_handler(CommandHandler('matchlist', get_list))
    dispatcher.add_handler(CommandHandler('update', update_event))
    dispatcher.add_handler(CommandHandler('join', join_event))
    dispatcher.add_handler(CommandHandler('leave', leave_event))
    dispatcher.add_handler(CommandHandler('remove', delete_event))
    # possibly other commands lol

    logger.info('Bot started')
    updater.start_polling()

    updater.idle()

if __name__ == '__main__':
    main()
