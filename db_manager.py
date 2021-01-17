from dataclasses import dataclass, field
from datetime import datetime, date, time
from pytz import timezone

import logging
import random
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


def find_match(match_id):
    '''Searches the database for the given match'''

    with open('matches_db.csv', 'r') as db:
        db_as_text = db.read()

    db_as_list = db_as_text.split('\n')

    for index, line in enumerate(db_as_list):
        values = line.split(',')

        if values[POSITIONS['match_id']] == match_id:
            chat_id, sport, date, time, duration = values[POSITIONS['chat_id']:POSITIONS['duration'] + 1]
            players_list = values[POSITIONS['first_player']:]
            match = Match(
                chat_id=chat_id,
                sport=sport,
                date=date,
                time=time,
                duration=duration,
                players_list=players_list
            )
            match.match_id = match_id

            return db_as_list, match, index

    raise KeyError(f'{match_id} not found')


def overwrite_line(db_as_list, target_index, match=None):
    '''Overwrites a line of the database with the given new one'''

    if match:

        newline = str(match)
        db_as_list[target_index] = newline

    else:  # when match is not specified it just deletes the line
        db_as_list.pop(target_index)

    updated_db = '\n'.join(db_as_list)

    with open('matches_db.csv', 'w') as db:
        db.write(updated_db)

    logger.info('database successfully updated')


def get_sport_type_info(sport):
    '''Retrieves infos about player numbers of a given sport.'''

    sport_dict = SPORT_TYPES[sport]
    required_players, maximum_number_players = sport_dict.values()

    return required_players, maximum_number_players


def get_missing_players_number(match_id):
    '''Returns the number of missing players.'''

    match = find_match(match_id)[1]
    sport = match.sport
    required_players = get_sport_type_info(sport)[0]
    number_of_players = len(match.players_list)
    missing_players = required_players - number_of_players

    if missing_players < 0:
        return 0

    return missing_players


def generate_key():
    '''Generates primary key for database.'''

    key = ''.join(random.choices(string.digits, k=4))
    return key


def store_in_db(match):
    '''Stores new matches in the database.'''

    match_id = generate_key()
    match.match_id = match_id
    line = f'{match}\n'

    with open('matches_db.csv', 'a') as db:
        db.write(line)

    logger.info(f'New match {match_id} added')

    return match_id


@dataclass
class Match:
    '''Class that represents matches stored in database.'''

    chat_id: int
    sport: str
    date: date
    time: time
    duration: time
    players_list: list
    timezone: timezone = field(default=timezone('Europe/Rome'))
    match_id: str = field(init=False)
    datetime: datetime = field(init=False)

    def __post_init__(self):

        self.convert_dates_and_times()
        self.datetime = datetime.combine(self.date, self.time)
        self.datetime = self.timezone.localize(self.datetime)

    def __str__(self):

        match_fields = [self.match_id, self.chat_id, self.sport, self.date, self.time, self.duration]
        match_fields.extend(self.players_list)

        return ','.join(map(str, match_fields))

    def is_in_the_past(self):
        '''Checks whether an event is in the past or not. If so, raise the proper exception.'''

        now = self.timezone.localize(datetime.now())

        if self.datetime < now:
            logger.debug(f'Event in the past check: {self.datetime} < {now}')

            return True

        return False

    def add_player(self, player):
        '''Adds a player who has joined the match.'''

        assert type(player) == str, 'Convert player id to string'
        self.players_list.append(player)

    def remove_player(self, player):
        '''Removes a player who has left the match.'''

        assert type(player) == str, 'Convert player id to string'
        self.players_list.remove(player)

    def convert_dates_and_times(self):
        '''Converts dates and times from the string format to the appropriate format.'''

        if type(self.date) == str:
            self.date = date.fromisoformat(self.date)

        if type(self.time) == str:
            self.time = time.fromisoformat(self.time)

        if type(self.duration) == str:
            self.duration = time.fromisoformat(self.duration)

    def get_time_to_event(self):
        '''Returns how much time is left since the beginning of the event.'''

        now = self.timezone.localize(datetime.now())
        time_left = self.datetime - now

        return time_left

