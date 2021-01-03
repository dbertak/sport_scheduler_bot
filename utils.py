from exceptions import DatabaseNotFoundError, MatchNotFoundError
from db_manager import find_match


def get_message_info(update):
    '''retrieves the relevant information from the message.'''

    text_message = update.message.text
    chat_id = update.effective_chat.id
    user_id = update.message.from_user.id
    return text_message, chat_id, user_id


def get_match_in_db(context, match_id, chat_id, user_id):
    '''Tries to find a match in the database, raises the proper exceptions in case of failure.'''

    try:
        db, match_line, index = find_match(match_id)

    except FileNotFoundError:
        raise DatabaseNotFoundError(context, chat_id)

    except KeyError:
        error_message = f'Match {match_id} not found'
        raise MatchNotFoundError(context, chat_id, match_id, error_message)

    return db, match_line, index

