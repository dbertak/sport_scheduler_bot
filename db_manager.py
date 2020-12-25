import csv
import logging
import random
import re
import string

from datetime import datetime, timedelta

from config import CONFIG

logger = logging.getLogger(__name__)

SPORT_TYPES = CONFIG['sport_types']

def parse_data(text):
    '''Gets data from telegram message'''

    command_match = re.match(r'^[\/a-z]+', text)

    if command_match:
        text = text[len(command_match.group()):]

    data = text.split(',')
    parsed_data = []

    for datum in data:
        stripped_datum = datum.strip()
        parsed_data.append(stripped_datum)

    return parsed_data

def generate_key():
    '''Generates primary key for database'''

    x = ''.join(random.choices(string.ascii_letters + string.digits, k=8))

    return x

def store_in_db(message_text, chat_id, user_id):
    '''Stores new matches in the database.'''

    parsed_data = parse_data(message_text)
    assert len(parsed_data) == 3, 'Wrong input size'

    primary_key = generate_key()
    sport, date_time, duration = parsed_data

    if sport not in SPORT_TYPES.keys():
        raise ValueError(f'Sport {sport} not implemented yet')

    with open('matches_db.csv', 'a') as db:
        writer = csv.writer(db)
        writer.writerow([primary_key, chat_id, sport, date_time, duration, user_id])
        logger.info(f'new match {primary_key} added')

    return primary_key

def update_match(text_message, user_id):
    '''Updates specific field of a given match.'''

    parsed_data = parse_data(text_message)
    match_id = parsed_data[0]
    field = parsed_data[1]
    new_entry = parsed_data[2]

    try:
        with open('matches_db.csv', 'r') as db:
            db_as_text = db.read()
    except FileNotFoundError:
        logger.error('Database not instantiated yet, impossible to update')
        raise FileNotFoundError

    db_as_list = db_as_text.split('\n')

    for index, line in enumerate(db_as_list):
        values = line.split(',')

        if values[0] == match_id:
            target_line = values
            target_index = index
            break
    else:
        logger.error('We cannot find your match in our db')
        raise KeyError(f'{match_id} not found')

    if str(user_id) not in target_line:
        raise PermissionError('User not allowed to modify this match')

    if field == 'sport':
        if new_entry not in SPORT_TYPES.keys():
            raise ValueError(f'Sport {new_entry} not implemented yet')

        target_line[2] = new_entry

    elif field == 'date':
        formatted_datum = new_entry.replace('/', '-')
        target_line[3] = new_entry

    elif field == 'duration':
        target_line[4] = new_entry

    else:
        logger.error(f'Unrecognized field {field}')
        raise ValueError(f'Unrecognized field {field}')

    db_as_list[target_index] = target_line

    with open('matches_db.csv', 'w') as db:
        writer = csv.writer(db)
        writer.writerows(db_as_list)
        logger.info(f'database successfully updated')
