from datetime import datetime, timedelta

import logging

from utils import delete_match
from config import CONFIG

logging.basicConfig(format=CONFIG['logging']['format'], level=CONFIG['logging']['level'])
logger = logging.getLogger(__name__)


class Reminder:

    def __init__(self, update, context, match):

        self.update = update
        self.match_context = context
        self.match = match
        self.set_alerts()

    def alert(self, context):
        '''Alerts users in the group until required number of players is reached.'''

        job = context.job
        time_left = self.match.get_time_to_event()
        time_left_str = str(time_left).split('.')[0]
        missing_players = self.match.get_missing_players_number()
        text = f'Match {self.match.match_id} requires {missing_players} additional players.'
        time_left_text = f'Match happening in {time_left_str}.'

        if missing_players > 0:
  
            text = f'{text}\n{time_left_text}'
            self.match_context.bot.send_message(
                chat_id=job.context,
                text=text
            )

    def last_day_alert(self, context):
        '''Sends a reminder saying that the match is going to happen the next day.'''

        job = context.job
        text = f'Reminder: the match {self.match.match_id} will take place tomorrow at this time.'
        self.match_context.bot.send_message(
            chat_id=job.context,
            text=text
        )

    def remove_match(self, context):
        '''Removes a match from the database after it has happened.'''

        delete_match(self.match.match_id)
        logger.info(f'Match {self.match.match_id} is happening right now. Removing it from database.')

    @staticmethod
    def remove_job(context, match_id):
        '''Remove jobs of a given match id.'''

        job_names = get_jobs_name(match_id) 

        for name in job_names:
            current_jobs = context.job_queue.get_jobs_by_name(name)

            if not current_jobs:
                logger.warning(f'Job associated to match {name} has been already removed')

            elif len(current_jobs) > 1:
                raise ValueError(f'There mustn\'t be more than one job per match_id {name}')

            else:
                current_jobs[0].schedule_removal()
                logger.info(f'Match {name} reminder has been disabled')

    def set_alerts(self):
        '''Add alerts to the queue.'''

        self.remove_job(self.match_context, self.match.match_id)
        chat_id = self.update.message.chat_id
        time_left = self.match.get_time_to_event()
        match_id, last_day_alert_job_name, remove_match_job_name = get_jobs_name(self.match.match_id)

        if time_left > timedelta(days=1):  # pointless to run such jobs if user scheduled an event within a day
            self.match_context.job_queue.run_repeating(
                self.alert,
                first=30,
                interval=timedelta(days=1),
                last=self.match.datetime - timedelta(hours=12),
                context=chat_id,
                name=match_id
            )
            self.match_context.job_queue.run_once(
                self.last_day_alert,
                when=self.match.datetime - timedelta(days=1),
                context=chat_id,
                name=last_day_alert_job_name
            )

        self.match_context.job_queue.run_once(
            self.remove_match,
            when=self.match.datetime,
            context=chat_id,
            name=remove_match_job_name
        )
        logger.info(f'Reminder for match {self.match.match_id} has been set.')


def get_jobs_name(match_id):
    '''Retrieves the job names to pass to the job scheduler.'''

    job_name = f'match_number_{match_id}'
    last_day_alert_job_name = f'{match_id}_last_day'
    remove_match_job_name = f'{match_id}_remove_match'

    return job_name, last_day_alert_job_name, remove_match_job_name

