from telegram import ParseMode
from datetime import datetime, timedelta

import logging

from config import CONFIG
from db_manager import (
    store_in_db,
    parse_message,
    parse_line,
    find_match,
    overwrite_line,
    check_players_number
)
from exceptions import (
    DatabaseNotFoundError,
    MatchNotFoundError,
    SportKeyError,
    DateTimeValueError,
    EventInThePastError,
    UnauthorizedUserError
)

SPORT_TYPES = CONFIG['sport_types']
FIRST_PLAYER_POSITION = 5
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
    text_message = update.message.text
    chat_id = update.effective_chat.id
    user_id = update.message.from_user.id
    parsed_data = parse_message(text_message)

    assert len(parsed_data) == 3, 'Wrong input size'
    sport, date_time, duration = parsed_data

    if sport not in SPORT_TYPES.keys():
        error_message = f'Sport {sport} not implemented yet'
        raise SportKeyError(context, chat_id, sport, error_message)

    try:
        event_date_time = datetime.strptime(date_time, "%d/%m/%Y %H:%M")

    except ValueError:
        raise DateTimeValueError(context, chat_id)

    present = datetime.now()

    if event_date_time < present:
        raise EventInThePastError(context, chat_id)

    match_id = store_in_db(chat_id, user_id, sport, date_time, duration)
    context.bot.send_message(
        chat_id=chat_id,
        text=f'Match {match_id} has been successfully created'
    )


def update_event(update, context):
    text_message = update.message.text
    chat_id = update.effective_chat.id
    user_id = update.message.from_user.id
    parsed_data = parse_message(text_message)

    assert len(parsed_data) == 3, 'Wrong input size'
    match_id, field, new_entry = parsed_data

    try:
        db_as_list, target_line, target_index = find_match(match_id)

    except FileNotFoundError:
        raise DatabaseNotFoundError(context, chat_id)

    except KeyError:
        error_message = f'Match {match_id} not found'
        raise MatchNotFoundError(context, chat_id, match_id, error_message)

    if str(user_id) not in target_line[FIRST_PLAYER_POSITION:]:
        raise UnauthorizedUserError(context, chat_id, match_id)

    if field == 'sport':

        if new_entry not in SPORT_TYPES.keys():
            error_message = f'Sport {sport} not implemented yet'
            raise SportKeyError(context, chat_id, sport, error_message)

        target_line[2] = new_entry

    elif field == 'date':

        try:
            event_date_time = datetime.strptime(new_entry, "%d/%m/%Y %H:%M")

        except ValueError:
            raise DateTimeValueError(context, chat_id)

        present = datetime.now()

        if event_date_time < present:
            raise EventInThePastError(context, chat_id)

        target_line[3] = new_entry

    elif field == 'duration':
        target_line[4] = new_entry

    else:
        logger.error(f'Unrecognized field {field}')
        context.bot.send_message(
            chat_id=chat_id,
            text='Unrecognized field, it is only possible to update sport type,'
                 'date/time and duration of the event',
            parse_mode=ParseMode.MARKDOWN
        )
        raise ValueError(f'Unrecognized field {field}')

    overwrite_line(db_as_list, target_index, target_line)

    context.bot.send_message(
        chat_id=chat_id,
        text=f'Match has been successfully updated'
    )
    logger.info('Match successfully updated')


def join_event(update, context):
    text_message = update.message.text
    chat_id = update.effective_chat.id
    user_id = update.message.from_user.id
    match_id = parse_message(text_message)[0]

    try:
        db, match_line, index = find_match(match_id)

    except FileNotFoundError:
        raise DatabaseNotFoundError(context, chat_id)

    except KeyError:
        error_message = f'Match {match_id} not found'
        raise MatchNotFoundError(context, chat_id, match_id, error_message)

    if str(user_id) in match_line[FIRST_PLAYER_POSITION:]:
        context.bot.send_message(
            chat_id=chat_id,
            text='User already joined the match'
        )
        raise ValueError('User already joined the match')

    else:
        match_line.append(user_id)
        overwrite_line(db, index, match_line)
        context.bot.send_message(
            chat_id=chat_id,
            text=f'User has successfully joined match {match_id}'
        )
        logger.info('User has successfully joined the match')

def leave_event(update, context):
    '''Allows the user the leave an event'''

    text_message = update.message.text
    chat_id = update.effective_chat.id
    user_id = update.message.from_user.id
    match_id = parse_message(text_message)[0]

    try:
        db, match_line, index = find_match(match_id)

    except FileNotFoundError:
        raise DatabaseNotFoundError(context, chat_id)

    except KeyError:
        error_message = f'Match {match_id} not found'
        raise MatchNotFoundError(context, chat_id, match_id, error_message)

    if str(user_id) in match_line[FIRST_PLAYER_POSITION:]:
        match_line.remove(str(user_id))
        overwrite_line(db, index, match_line)
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

    text_message = update.message.text
    chat_id = update.effective_chat.id
    user_id = update.message.from_user.id
    match_id = parse_message(text_message)[0]

    try:
        db, match_line, index = find_match(match_id)

    except FileNotFoundError:
        raise DatabaseNotFoundError(context, chat_id)

    except KeyError:
        error_message = f'Match {match_id} not found'
        raise MatchNotFoundError(context, chat_id, match_id, error_message)

    if str(user_id) in match_line[FIRST_PLAYER_POSITION:]:
        overwrite_line(db, index)
        context.bot.send_message(
            chat_id=chat_id,
            text=f'Match {match_id} removed from database'
        )
        logger.info('Match removed from database')

    else:
        raise UnauthorizedUserError(context, chat_id, match_id)
 
