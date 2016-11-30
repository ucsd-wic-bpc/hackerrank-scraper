from scraper import Scraper
import json

CONFIG_LEADERBOARD_URL_KEY = 'leaderboard_url'
CONFIG_USERNAME_KEY = 'username'
CONFIG_PASSWORD_KEY = 'password'

# First, load the config
with open('config.json', 'r') as f:
    config = json.loads(f.read())


scr = Scraper(config[CONFIG_USERNAME_KEY],
              config[CONFIG_PASSWORD_KEY],
              config[CONFIG_LEADERBOARD_URL_KEY])

scr.login()

for competitor in scr.scrape():
    print(competitor)
