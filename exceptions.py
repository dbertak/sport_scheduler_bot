class DatabaseNotFoundError(FileNotFoundError):
    '''To be raised when database has not been created yet.'''

    def __init__(self, context, chat_id, message='Database not found'):
        self.message = message
        self.text = 'Database is empty, try to create a new match first with /newmatch'
        context.bot.send_message(chat_id, self.text)
        super().__init__(self.message)


class MatchNotFoundError(KeyError):
    '''To be raised when match is not found in the database.'''

    def __init__(self, context, chat_id, match_id, message='Match not found'):
        self.message = message
        self.text = f'Your match {match_id} is not in our database, check for possible typos or create a new match with /newmatch'
        context.bot.send_message(chat_id, self.text)
        super().__init__(self.message)


class SportKeyError(KeyError):
    '''To be raised when user types a sport not available yet.'''

    def __init__(self, context, chat_id, sport, message='Sport not implemented yet'):
        self.message = message
        self.text = f'Unrecognized sport field {sport}: choose an available sport, find them with /showsports'
        context.bot.send_message(chat_id, self.text)
        super().__init__(self.message)


class DateValueError(ValueError):
    '''To be raised when user types date and time format wrong.'''

    def __init__(self, context, chat_id, message='Wrong date format'):
        self.message = message
        self.text = 'Wrong date format, please use dd/mm/yyyy'
        context.bot.send_message(chat_id, self.text)
        super().__init__(self.message)


class TimeValueError(ValueError):
    '''To be raised when user types date and time format wrong.'''

    def __init__(self, context, chat_id, message='Wrong time format'):
        self.message = message
        self.text = 'Wrong time format, please use hh:mm'
        context.bot.send_message(chat_id, self.text)
        super().__init__(self.message)


class EventInThePastError(ValueError):
    '''To be raised when user schedules an event in the past.'''

    def __init__(self, context, chat_id, message='Event in the past'):
        self.message = message
        self.text = 'Event cannot be in the past'
        context.bot.send_message(chat_id, self.text)
        super().__init__(self.message)


class UnauthorizedUserError(PermissionError):
    '''To be raised when user tries to access an event without permission.'''

    def __init__(self, context, chat_id, match_id, message='User not allowed to modify this match'):
        self.message = message
        self.text = f'User not allowed to modify match {match_id}'
        context.bot.send_message(chat_id, self.text)
        super().__init__(self.message)


class InputSizeError(ValueError):
    '''To be raised when user types too many fields in a command.'''

    def __init__(self, context, chat_id, fields_number, expected_number, message='Too many values to unpack'):
        self.message = message
        self.text = f'Unexepected number of fields {fields_number} for this command, correct number: {expected_number}'
        context.bot.send_message(chat_id, self.text)
        super().__init__(self.message)

