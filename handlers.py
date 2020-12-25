from telegram import ParseMode

from db_manager import store_in_db, update_match

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


def new_match(update, context):
    match_raw_data = update.message.text
    chat_id = update.effective_chat.id
    user_id = update.message.from_user.id
    try:
        match_id = store_in_db(match_raw_data, chat_id, user_id)
        context.bot.send_message(
            chat_id=chat_id,
            text=f'Match {match_id} has been successfully created'
        )
    except ValueError:
        context.bot.send_message(
            chat_id=chat_id,
            text='Sport not implemented yet or date and time expressed in the wrong format.\n'
                 'Date and time must be expressed in dd-mm-yyyy hh:mm',
            parse_mode=ParseMode.MARKDOWN
        )


def update_event(update, context):
    match_raw_data = update.message.text
    chat_id = update.effective_chat.id
    user_id = update.message.from_user.id

    try:
        update_match(match_raw_data, user_id)
        context.bot.send_message(
            chat_id=chat_id,
            text=f'Match has been successfully updated'
        )
    except FileNotFoundError:
        context.bot.send_message(
            chat_id=chat_id,
            text=f'Database is empty, try to create a new match first. Type /newmatch'
        )
    except KeyError:
        context.bot.send_message(
            chat_id=chat_id,
            text=f'Your match is not in our database, check for possible typos or create a new match with /newmatch'
        )
    except ValueError:
        context.bot.send_message(
            chat_id=chat_id,
            text='Unrecognized fields, choose available sports or write date and time in the correct format',
            parse_mode=ParseMode.MARKDOWN
        )
