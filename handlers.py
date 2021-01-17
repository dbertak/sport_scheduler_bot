from datetime import datetime
from telegram import ParseMode

import logging

from utils import (
    get_message_info,
    get_match_in_db
)
from db_manager import (
    SPORT_TYPES,
    Match,
    store_in_db,
    overwrite_line
)
from exceptions import (
    SportKeyError,
    DateValueError,
    TimeValueError,
    EventInThePastError,
    InputSizeError,
    UnauthorizedUserError
)
from reminder import Reminder


logger = logging.getLogger(__name__)


def start(update, context):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Hi! I am here to help you scheduling sport matches with your friends\n'
             'Type /help for more information'
             'GitHub: [SportSchedulerBot](https://github.com/dbertak/sport_scheduler_bot)',
        parse_mode=ParseMode.MARKDOWN
        )


def show_help(update, context):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='*First of all, add this bot to your group chat*\n'
             'Schedule a new match with /newmatch command (prints match id)\n'
             'syntax: /newmatch <sport> <date> <time> <duration>\n'
             'e.g. /newmatch tennis 10/03/2021 17:30 1:30\n'
             'Other commands:\n'
             '/update, allows to modify type of sport, date/time or match duration.\n'
             'syntax: /update <match_id> <field> <new value>\n'
             'e.g. /update 2039 time 20:15 (changes the time of event 2039 to 20:15)\n'
             '/showsports, prints all the available sports.\n'
             '/join <match id>, to join a match\n'
             '/leave <match id>, to abandon a match\n'
             '/remove <match id>, to cancel a match\n'
        )


def show_sports(update, context):
    '''Prints available sports'''

    text = ', '.join(SPORT_TYPES.keys())
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text
    )


def new_match(update, context):
    chat_id, user_id = get_message_info(update)
    parsed_data = context.args 

    if len(parsed_data) != 4: 
        raise InputSizeError(context, chat_id, len(parsed_data), 4)

    sport, date, time, duration = parsed_data

    if sport not in SPORT_TYPES.keys():
        error_message = f'Sport {sport} not implemented yet'
        raise SportKeyError(context, chat_id, sport, error_message)

    try:
        event_date = datetime.strptime(date, "%d/%m/%Y").date()

    except ValueError:
        raise DateValueError(context, chat_id)

    try:
        event_time = datetime.strptime(time, "%H:%M").time()

    except ValueError:
        raise TimeValueError(context, chat_id)

    try:
        event_duration = datetime.strptime(duration, "%H:%M").time()

    except ValueError:
        raise TimeValueError(context, chat_id)

    match = Match(
        chat_id=chat_id,
        sport=sport,
        date=event_date,
        time=event_time,
        duration=event_duration,
        players_list=[user_id]
    )

    if match.is_in_the_past():
        raise EventInThePastError(context, chat_id)

    match_id = store_in_db(match)
    context.bot.send_message(
        chat_id=chat_id,
        text=f'Match {match_id} has been successfully created,\n'
             f'{match_id} must be specified when using the commands /update, /join, /leave and /remove as first argument.'
    )

    Reminder(update, context, match)


def update_event(update, context):
    chat_id, user_id = get_message_info(update)
    parsed_data = context.args 

    if len(parsed_data) != 3: 
        raise InputSizeError(context, chat_id, len(parsed_data), 3)

    match_id, field, new_entry = parsed_data

    db_as_list, match, target_index = get_match_in_db(context, match_id, chat_id, user_id)

    if str(user_id) not in match.players_list:
        raise UnauthorizedUserError(context, chat_id, match_id)

    if field == 'sport':

        if new_entry not in SPORT_TYPES.keys():
            error_message = f'Sport {new_entry} not implemented yet'
            raise SportKeyError(context, chat_id, new_entry, error_message)

        match.sport = new_entry
        Reminder(update, context, match)

    elif field == 'date':

        try:
            event_date = datetime.strptime(new_entry, "%d/%m/%Y").date()

        except ValueError:
            raise DateValueError(context, chat_id)

        match.date = event_date
        match.__post_init__()

        if match.is_in_the_past():
            raise EventInThePastError(context, chat_id)

        Reminder(update, context, match)

    elif field == 'time':

        try:
            event_time = datetime.strptime(new_entry, "%H:%M").time()

        except ValueError:
            raise TimeValueError(context, chat_id)

        match.time = event_time
        match.__post_init__()

        if match.is_in_the_past():
            raise EventInThePastError(context, chat_id)

        Reminder(update, context, match)

    elif field == 'duration':

        try:
            event_duration = datetime.strptime(new_entry, "%H:%M").time()

        except ValueError:
            raise TimeValueError(context, chat_id)

        match.duration = event_duration

    else:
        logger.error(f'Unrecognized field {field}')
        context.bot.send_message(
            chat_id=chat_id,
            text='Unrecognized field, it is only possible to update sport type,'
                 'date/time and duration of the event',
            parse_mode=ParseMode.MARKDOWN
        )
        raise ValueError(f'Unrecognized field {field}')

    overwrite_line(db_as_list, target_index, match)

    context.bot.send_message(
        chat_id=chat_id,
        text=f'Match has been successfully updated'
    )
    logger.info('Match successfully updated')


def join_event(update, context):
    chat_id, user_id = get_message_info(update)
    parsed_data = context.args 

    if len(parsed_data) != 1: 
        raise InputSizeError(context, chat_id, len(parsed_data), 1)

    match_id = parsed_data[0]
    db, match, index = get_match_in_db(context, match_id, chat_id, user_id)

    if str(user_id) in match.players_list:
        context.bot.send_message(
            chat_id=chat_id,
            text='User already joined the match'
        )
        raise ValueError('User already joined the match')

    else:
        match.add_player(str(user_id))
        overwrite_line(db, index, match)
        context.bot.send_message(
            chat_id=chat_id,
            text=f'User has successfully joined match {match_id}'
        )
        logger.info('User has successfully joined the match')


def leave_event(update, context):
    '''Allows the user the leave an event'''

    chat_id, user_id = get_message_info(update)
    parsed_data = context.args 

    if len(parsed_data) != 1: 
        raise InputSizeError(context, chat_id, len(parsed_data), 1)

    match_id = parsed_data[0]
    db, match, index = get_match_in_db(context, match_id, chat_id, user_id)

    if str(user_id) in match.players_list:

        match.remove_player(str(user_id))
        overwrite_line(db, index, match)
        context.bot.send_message(
            chat_id=chat_id,
            text='User removed from the match'
        )
        logger.info('User has successfully left the match')

    else:
        context.bot.send_message(
            chat_id=chat_id,
            text='User was not among the players already,'
                 ' check for typos in the match ID',
        )
        raise KeyError('User not found')


def delete_event(update, context):
    '''Allows user to remove an event.'''

    chat_id, user_id = get_message_info(update)
    parsed_data = context.args 

    if len(parsed_data) != 1: 
        raise InputSizeError(context, chat_id, len(parsed_data), 1)

    match_id = parsed_data[0]
    db, match, index = get_match_in_db(context, match_id, chat_id, user_id)

    if str(user_id) in match.players_list:
        overwrite_line(db, index)
        context.bot.send_message(
            chat_id=chat_id,
            text=f'Match {match_id} removed from database'
        )
        logger.info('Match removed from database')
        Reminder.remove_job(context, match.match_id)

    else:
        raise UnauthorizedUserError(context, chat_id, match_id)

