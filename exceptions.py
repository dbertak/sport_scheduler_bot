def send_message(context, chat_id, text, markdown=None):
    '''Sends the error message to Telegram user'''

    context.bot.send_message(
        chat_id=chat_id,
        text=text,
        parse_mode=markdown
    )


class DatabaseNotFoundError(FileNotFoundError):
    '''To be raised when database has not been created yet.'''

    def __init__(self, context, chat_id, message='Database not found'):
        self.message = message
        self.text = 'Database is empty, try to create a new match first with /newmatch'
        send_message(context, chat_id, self.text)
        super().__init__(self.message)


class MatchNotFoundError(KeyError):
    '''To be raised when match is not found in the database.'''

    def __init__(self, context, chat_id, match_id, message='Match not found'):
        self.message = message
        self.text = f'Your match {match_id} is not in our database, check for possible typos or create a new match with /newmatch'
        send_message(context, chat_id, self.text)
        super().__init__(self.message)


class SportKeyError(KeyError):
    '''To be raised when user types a sport not available yet.'''

    def __init__(self, context, chat_id, sport, message='Sport not implemented yet'):
        self.message = message
        self.text = f'Unrecognized sport field {sport}: choose an available sport, find them with /showsports'
        send_message(context, chat_id, self.text)
        super().__init__(self.message)


class DateTimeValueError(ValueError):
    '''To be raised when user types date and time format wrong.'''

    def __init__(self, context, chat_id, message='Wrong date time format'):
        self.message = message
        self.text = 'Wrong date and time format, please use dd/mm/yyyy hh:mm'
        send_message(context, chat_id, self.text)
        super().__init__(self.message)

class EventInThePastError(ValueError):
    '''To be raised when user schedules an event in the past'''

    def __init__(self, context, chat_id, message='Event in the past'):
        self.message = message
        self.text = 'Event cannot be in the past'
        send_message(context, chat_id, self.text)
        super().__init__(self.message)
