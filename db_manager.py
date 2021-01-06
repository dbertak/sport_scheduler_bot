import csv
import logging
import random
import re
import string

from config import SPORT_CONFIG

SPORT_TYPES = SPORT_CONFIG['sport_types']
POSITIONS = {
    'match_id': 0,
    'chat_id': 1,
    'sport': 2,
    'date': 3,
    'time': 4,
    'duration': 5,
    'first_player': 6
}

logger = logging.getLogger(__name__)


def generate_key():
    '''Generates primary key for database.'''

    x = ''.join(random.choices(string.digits, k=4))
    return x


def get_field_value(match_id, field):
    '''Returns the value associated to a given field of a given match.'''

    _, values, __ = find_match(match_id)
    return values[POSITIONS[field]]


def find_match(match_id):
    '''Searches the database for the given match'''

    try:

        with open('matches_db.csv', 'r') as db:
            db_as_text = db.read()

    except FileNotFoundError:
        logger.error('Database not instantiated yet, impossible to update')
        raise FileNotFoundError

    db_as_list = db_as_text.split('\n')

    for index, line in enumerate(db_as_list):
        values = line.split(',')

        if values[POSITIONS['match_id']] == match_id:
            return db_as_list, values, index

    logger.error(f'{match_id} not found')
    raise KeyError()


def overwrite_line(db_as_list, target_index, updated_line=None):
    '''Overwrites a line of the database with the given new one'''

    if updated_line:
        db_as_list[target_index] = updated_line

    else:  # when updated line is not specified it just deletes the line
        db_as_list.pop(target_index)

    with open('matches_db.csv', 'w') as db:
        writer = csv.writer(db)
        writer.writerows(db_as_list)
        logger.info('database successfully updated')


def get_sport_type_info(sport):
    '''Retrieves infos about player numbers of a given sport.'''

    sport_dict = SPORT_TYPES.get(sport)
    required_players = sport_dict['required_players']
    maximum_number_players = sport_dict['maximum_number_players']

    return required_players, maximum_number_players


def get_missing_players_number(match_id):
    '''Returns the number of missing players.'''

    _, match_line, __ = find_match(match_id)
    sport = match_line[POSITIONS['sport']]
    required_players, ___ = get_sport_type_info(sport)
    number_of_players = len(match_line[POSITIONS['first_player']:])

    missing_players = required_players - number_of_players

    if missing_players < 0:
        return 0

    return missing_players


def store_in_db(chat_id, user_id, sport, date, time, duration):
    '''Stores new matches in the database.'''

    primary_key = generate_key()

    with open('matches_db.csv', 'a') as db:
        writer = csv.writer(db)
        writer.writerow([primary_key, chat_id, sport, date, time, duration, user_id])
        logger.info(f'new match {primary_key} added')

    return primary_key

