from exceptions import DatabaseNotFoundError, MatchNotFoundError, UnauthorizedUserError
from db_manager import find_match


def get_message_info(update):
    '''Retrieves the relevant information from the message.'''

    chat_id = update.effective_chat.id
    user_id = update.message.from_user.id
    return chat_id, user_id


def get_match_in_db(context, match_id, chat_id):
    '''Tries to find a match in the database, raises the proper exceptions in case of failure.'''

    try:
        db, match, index = find_match(match_id, chat_id)

    except FileNotFoundError:
        raise DatabaseNotFoundError(context, chat_id)

    except PermissionError:
        error_message = 'User not allowed to modify matches from other groups'
        raise UnauthorizedUserError(context, chat_id, match_id, error_message)

    except KeyError:
        error_message = f'Match {match_id} not found'
        raise MatchNotFoundError(context, chat_id, match_id, error_message)

    return db, match, index

