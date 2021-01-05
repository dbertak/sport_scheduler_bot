import csv
import logging
import random
import re
import string

from config import CONFIG

FIRST_PLAYER_POSITION = 5
SPORT_TYPES = CONFIG['sport_types']
SPORT_POSITION = 2

logger = logging.getLogger(__name__)


def generate_key():
    '''Generates primary key for database.'''

    x = ''.join(random.choices(string.digits, k=4))
    return x


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

        if values[0] == match_id:
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


# TODO:
#    def get_sport_type_info(sport):
#        '''Retrieves infos about player numbers of a given sport.'''
#
#        sport_dict = SPORT_TYPES.get(sport)
#        required_players = sport_dict['required_players']
#        maximum_number_players = sport_dict['maximum_number_players']
#
#        return required_players, maximum_number_players
#
#
#    def get_missing_players_number(match_id):
#        '''Returns the number of missing players.'''
#
#        _, match_line, __ = find_match(match_id)
#        sport = match_line[SPORT_POSITION]
#        required_players, ___ = get_sport_type_info(sport)
#        number_of_players = len(match_line[FIRST_PLAYER_POSITION:])
#
#        missing_players = required_players - number_of_players
#
#        if missing_players < 0:
#            return 0
#
#        return missing_players


def store_in_db(chat_id, user_id, sport, date, time, duration):
    '''Stores new matches in the database.'''

    primary_key = generate_key()

    with open('matches_db.csv', 'a') as db:
        writer = csv.writer(db)
        writer.writerow([primary_key, chat_id, sport, date, time, duration, user_id])
        logger.info(f'new match {primary_key} added')

    return primary_key

