from telegram import ParseMode

import datetime as dt
import logging

from utils import (
    get_message_info,
    get_match_in_db
)
from db_manager import (
    POSITIONS,
    SPORT_TYPES,
    store_in_db,
    overwrite_line,
    get_missing_players_number
)
from exceptions import (
    SportKeyError,
    DateValueError,
    TimeValueError,
    EventInThePastError,
    InputSizeError,
    UnauthorizedUserError
)

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
             'Schedule a new match with /newmatch command (prints match id)\n'
             'Other commands:\n'
             '/update, allows to modify type of sport, date/time or match duration.\n'
             '/showsports, prints all the available sports.\n'
             '/join, to join matches\n'
             '/leave, to abandon matches\n'
             '/remove, to cancel a match\n'
             'GitHub: [SportSchedulerBot](https://github.com/dbertak/sport_scheduler_bot)',
        parse_mode=ParseMode.MARKDOWN
        )


def show_sports(update, context):
    '''Prints available sports'''

    text = ', '.join(sport for sport in SPORT_TYPES.keys())
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
        event_date = dt.datetime.strptime(date, "%d/%m/%Y").date()

    except ValueError:
        raise DateValueError(context, chat_id)

    try:
        event_time = dt.datetime.strptime(time, "%H:%M").time()

    except ValueError:
        raise TimeValueError(context, chat_id)

    try:
        event_duration =dt.datetime.strptime(duration, "%H:%M").time()

    except ValueError:
        raise TimeValueError(context, chat_id)

    present = dt.datetime.now()
    event_date_time = dt.datetime.combine(event_date, event_time)

    if event_date_time < present:
        raise EventInThePastError(context, chat_id)

    match_id = store_in_db(chat_id, user_id, sport, date, time, duration)
    context.bot.send_message(
        chat_id=chat_id,
        text=f'Match {match_id} has been successfully created,\n'
             f'{match_id} must be specified when using the commands /update, /join, /leave and /remove as first argument.'
    )

    missing_players = get_missing_players_number(match_id)
    context.bot.send_message(
        chat_id=chat_id,
        text=f'Match {match_id} requires {missing_players} additional players'
    )

def update_event(update, context):
    chat_id, user_id = get_message_info(update)
    parsed_data = context.args 

    if len(parsed_data) != 3: 
        raise InputSizeError(context, chat_id, len(parsed_data), 3)

    match_id, field, new_entry = parsed_data

    db_as_list, target_line, target_index = get_match_in_db(context, match_id, chat_id, user_id)

    if str(user_id) not in target_line[POSITIONS['first_player']:]:
        raise UnauthorizedUserError(context, chat_id, match_id)

    if field == 'sport':

        if new_entry not in SPORT_TYPES.keys():
            error_message = f'Sport {new_entry} not implemented yet'
            raise SportKeyError(context, chat_id, new_entry, error_message)

        target_line[POSITIONS['sport']] = new_entry

    elif field == 'date':

        try:
         event_date = dt.datetime.strptime(new_entry, "%d/%m/%Y").date()

        except ValueError:
            raise DateValueError(context, chat_id)

        present = dt.date.today()

        if event_date < present:
            raise EventInThePastError(context, chat_id)

        target_line[POSITIONS['date']] = new_entry

    elif field == 'time':

        try:
            event_time = dt.datetime.strptime(new_entry, "%H:%M").time()

        except ValueError:
            raise TimeValueError(context, chat_id)

        target_line[POSITIONS['time']] = new_entry

    elif field == 'duration':

        try:
            event_duration = dt.datetime.strptime(new_entry, "%H:%M").time()

        except ValueError:
            raise TimeValueError(context, chat_id)

        target_line[POSITIONS['duration']] = new_entry

    else:
        logger.error(f'Unrecognized field {field}')
        context.bot.send_message(
            chat_id=chat_id,
            text='Unrecognized field, it is only possible to update sport type,'
                 'date/time and duration of the event',
            parse_mode=ParseMode.MARKDOWN
        )
        raise ValueError(f'Unrecognized field {field}')

    new_line = ','.join(map(str, target_line))
    overwrite_line(db_as_list, target_index, new_line)

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
    db, match_line, index = get_match_in_db(context, match_id, chat_id, user_id)
    players_list = match_line[POSITIONS['first_player']:]

    if str(user_id) in players_list:
        context.bot.send_message(
            chat_id=chat_id,
            text='User already joined the match'
        )
        raise ValueError('User already joined the match')

    else:
        match_line.append(user_id)
        new_line = ','.join(map(str, match_line))
        overwrite_line(db, index, new_line)
        context.bot.send_message(
            chat_id=chat_id,
            text=f'User has successfully joined match {match_id}'
        )
        logger.info('User has successfully joined the match')
        missing_players = get_missing_players_number(match_id)

        if missing_players > 0:
            context.bot.send_message(
                chat_id=chat_id,
                text=f'Match {match_id} requires {missing_players} additional players'
            )

def leave_event(update, context):
    '''Allows the user the leave an event'''

    chat_id, user_id = get_message_info(update)
    parsed_data = context.args 

    if len(parsed_data) != 1: 
        raise InputSizeError(context, chat_id, len(parsed_data), 1)

    match_id = parsed_data[0]
    db, match_line, index = get_match_in_db(context, match_id, chat_id, user_id)
    players_list = match_line[POSITIONS['first_player']:]

    if str(user_id) in players_list:
        players_list.remove(str(user_id))
        match_line[POSITIONS['first_player']:] = players_list
        new_line = ','.join(map(str, match_line))
        overwrite_line(db, index, new_line)
        context.bot.send_message(
            chat_id=chat_id,
            text='User removed from the match'
        )
        logger.info('User has successfully left the match')

        missing_players = get_missing_players_number(match_id)

        if missing_players > 0:
            context.bot.send_message(
                chat_id=chat_id,
                text=f'Match {match_id} requires {missing_players} additional players'
            )

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
    db, match_line, index = get_match_in_db(context, match_id, chat_id, user_id)
    players_list = match_line[POSITIONS['first_player']:]

    if str(user_id) in players_list:
        overwrite_line(db, index)
        context.bot.send_message(
            chat_id=chat_id,
            text=f'Match {match_id} removed from database'
        )
        logger.info('Match removed from database')

    else:
        raise UnauthorizedUserError(context, chat_id, match_id)
 
