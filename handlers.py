from telegram import ParseMode

import logging


logger = logging.getLogger(__name__)


def start(update, context):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Hi! I am here to help you scheduling sport matches with your friends\n'
             'Type /help for more information'
        )


def show_help(update, context):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='*First of all, add this bot to your group chat*\n'
              # more instructions
              'GitHub: [SportSchedulerBot](https://github.com/dbertak/sport_scheduler_bot)',
        parse_mode=ParseMode.MARKDOWN
        )
