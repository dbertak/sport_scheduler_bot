import json

with open('config.json', 'r') as file:
    CONFIG = json.loads(file.read())

with open('sport_config.json', 'r') as file:
    SPORT_CONFIG = json.loads(file.read())
