from lazy_ticker.tda_scraper import get_instruments
from lazy_ticker.schemas import InstrumentsList
from lazy_ticker.database import LazyDB
from string import ascii_uppercase
from random import choices
from time import time

import re


def build_watchlist_table():
    tweets = LazyDB.get_all_tweets_sorted_by_published_time()
    LazyDB.add_to_watchlist(tweets)


# build_watchlist_table()


def divide_chunks(container, size):
    for position in range(0, len(container), size):
        yield container[position : position + size]


from pprint import pprint as print
from time import sleep
from typing import Dict
from enum import Enum
import pendulum


class TimeFrame(str, Enum):
    MONTHS = "months"
    WEEKS = "weeks"
    DAYS = "days"
    HOURS = "hours"

    def convert_to_period(self, amount: int = 1) -> Dict[str, int]:
        return {self.value: amount}


tf = TimeFrame.MONTHS
print(tf)
print(tf.value)

# def get_periods
dt = pendulum.now("UTC")
amount = tf.convert_to_period()

# A period is the difference between 2 instances
period = dt - dt.subtract(**amount)

# A period is iterable
for dt in period:
    print(dt)


#
# while True:
#
#     watch = LazyDB.get_watchlist_symbols_within_last_month()
#     print("=============month============")
#     print(watch)
#     watch = LazyDB.get_watchlist_symbols_within_last_week()
#     print("=============week============")
#     print(watch)
#     watch = LazyDB.get_watchlist_symbols_within_last_day()
#     print("=============day============")
#     print(watch)
#     watch = LazyDB.get_watchlist_symbols_within_last_hour()
#     print("=============hour============")
#     print(watch)
#     sleep(30)
# build_watchlist_table()

#
#
# start = time()
#
#
# valid_instruments = LazyDB.get_instruments()
#
# if valid_instruments:
#     LazyDB.update_tweet_validation_column(valid_instruments)
#
# uncheck_symbols = LazyDB.get_all_symbols_from_unchecked_tweets()
#
# if uncheck_symbols:
#     for chunk in divide_chunks(uncheck_symbols, 500):
#         valid = get_instruments(chunk).dict()["instruments"]
#         LazyDB.add_instruments(valid)
#
#     valid_instruments = LazyDB.get_instruments()
#     LazyDB.update_tweet_validation_column(valid_instruments)
#
# LazyDB.delete_tweets_where_validation_column_is_false()
#
#
# end = time()
# print(end - start)

exit()

from lazy_ticker.paths import DATA_DIRECTORY
import shutil
import requests
import pendulum

URL = "http://localhost/user"

# IDEA: restor users from old data flag
# NOTE: Restore users from last states.

if DATA_DIRECTORY.exists():
    users = list(set(path.stem for path in DATA_DIRECTORY.glob("**/*.json")))
    for user in users:
        resp = requests.post(f"{URL}/{user}")
        print(resp)


# NOTE: Useful for cleanup. cleanup folders older than 24 hours utc time.
# date_paths = list(DATA_DIRECTORY.glob("*"))
date_paths = list(set(path.stem for path in DATA_DIRECTORY.glob("*")))

for path in date_paths:

    dir_dt = pendulum.from_format(path, "YYYY_MM_DD", tz="UTC")
    older_than_yesterday = dir_dt < pendulum.yesterday(tz="UTC")

    if older_than_yesterday:
        # shutil.rmtree(path)
        print(path, "is too old cleaning up")


exit()

from lazy_ticker.models import TwitterUsersTable, TwitterSymbolsTable
from lazy_ticker.schemas import (
    TwitterUserSchema,
    TwitterSymbolSchema,
    TwitterSymbolList,
    TweetSchema,
)
from lazy_ticker.twitter_scraper import scrape_users_tweets, scrape_user_id
from lazy_ticker.database import LazyDB

import pydantic
from typing import List

#
# #
# x = scrape_user_id("dgnsrek")
# print(x)
from pathlib import Path
import json

#
# input_path = Path("data/2020_06_19/tweets/1592525820/seekingalpha.json")
# print(input_path)
# print(input_path.exists())
#
# with open(input_path, mode="r") as read_file:
#     tweets_from_file = json.load(read_file)  # list of dictionaries
#     # tweets_from_file = pydantic.parse_obj_as(List[TwitterSymbolSchema], tweets_from_file)
#
# from pprint import pprint as print
#
# print(tweets_from_file)
# print(type(tweets_from_file))
# print(type(tweets_from_file))
# exists = LazyDB.check_all_tweets_exists(tweets_from_file)
# print(exists)
#
# for tweet in tweets_from_file:
#     print(tweet["tweet_id"])
#

# tweet_id = 1273041703193112579
tweet_id = None
from pprint import pprint as print


scraped_tweets = []
for tweet in scrape_users_tweets("seekingalpha", max_tickers=10, break_on_id=tweet_id):
    scraped_tweets += tweet.get_twitter_symbols()

print(TwitterSymbolList(tweets=scraped_tweets).json())

for user in LazyDB.get_all_users():
    print(user.last_tweet_id)
    print(user.name)
    print(user)
from time import sleep
from random import random

while True:
    t = random()
    print(t)
    sleep(t)
