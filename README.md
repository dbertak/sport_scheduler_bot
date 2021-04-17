# sport_scheduler_bot
Telegram bot

This is my first attempt to develop a bot that schedules sport matches among friends.

## Installation

Clone this repository somewhere in your machine.

Be sure to have at least Python 3.7 installed on your machine.
Set your Python virtual environment (recommended):

Install [venv](https://docs.python.org/3/library/venv.html)

```
$ python3 -m venv <envinroment_name>
$ source <envinroment_name>/bin/activate
```

Install [python-telegram-bot API](https://github.com/python-telegram-bot/python-telegram-bot)

[Create a new bot](https://core.telegram.org/bots#6-botfather) via Bot Father and keep the token 
Link : <https://t.me/botfather>

Put the token in `config.json` file.


```
$ cd <your_local_repo_directory> 
$ python3 main.py
```

## Dependencies

List of python libraries:

- dataclasses
- datetime
- json
- logging
- python-telegram-bot
- pytz


## How to start

Now you are ready to use the bot! Add it to a telegram group chat and type /start
