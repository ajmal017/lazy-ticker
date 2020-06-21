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

watch = LazyDB.get_watchlist_symbols_within_last_month()
print("=============month============")
print(watch)
watch = LazyDB.get_watchlist_symbols_within_last_week()
print("=============week============")
print(watch)

watch = LazyDB.get_watchlist_symbols_within_last_day()
print("=============day============")
print(watch)
watch = LazyDB.get_watchlist_symbols_within_last_hour()
print("=============hour============")
print(watch)
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
