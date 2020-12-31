import csv
import logging
import random
import re
import string


logger = logging.getLogger(__name__)


def parse_line(line):
    '''Parses a comma separated line'''

    data = line.split(',')
    parsed_data = []

    for datum in data:
        stripped_datum = datum.strip()
        parsed_data.append(stripped_datum)

    return parsed_data


def parse_message(text):
    '''Gets data from telegram message'''

    command_match = re.match(r'^[\/a-z]+', text)

    if command_match:
        text = text[len(command_match.group()):]

    parsed_data = parse_line(text)
    return parsed_data


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

    logger.error('We cannot find your match in our db')
    raise KeyError(f'{match_id} not found')


def overwrite_line(db_as_list, target_line, target_index):
    '''Overwrites a line of the database with the given new one'''

    db_as_list[target_index] = target_line

    with open('matches_db.csv', 'w') as db:
        writer = csv.writer(db)
        writer.writerows(db_as_list)
        logger.info(f'database successfully updated')

# TODO:
    # def check_players_number(match_id):
        #'''Controls whether a satisfying number of players is reached or not.'''

        # _, match_line, __ = find_match(match_id)
        # data = parse_line(match_line)

def store_in_db(chat_id, user_id, sport, date_time, duration):
    '''Stores new matches in the database.'''

    primary_key = generate_key()

    with open('matches_db.csv', 'a') as db:
        writer = csv.writer(db)
        writer.writerow([primary_key, chat_id, sport, date_time, duration, user_id])
        logger.info(f'new match {primary_key} added')

    return primary_key
