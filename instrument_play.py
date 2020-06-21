from lazy_ticker.tda_scraper import get_instruments
from lazy_ticker.schemas import InstrumentsList
from lazy_ticker.database import LazyDB
from string import ascii_uppercase
from random import choices
from time import time

import re


def divide_chunks(container, size):
    for position in range(0, len(container), size):
        yield container[position : position + size]


#
#
# start = time()
#
#
# valid_instruments = LazyDB.get_instruments()
#
# if valid_instruments:
#     LazyDB.update_tweets(valid_instruments)
#
# uncheck_symbols = LazyDB.get_uncheck_symbols_from_tweets()
#
# if uncheck_symbols:
#     for chunk in divide_chunks(uncheck_symbols, 500):
#         valid = get_instruments(chunk).dict()["instruments"]
#         LazyDB.add_instruments(valid)
#
#     valid_instruments = LazyDB.get_instruments()
#     LazyDB.update_tweets(valid_instruments)
#
# LazyDB.delete_invalid_tweets()
#
#
# end = time()
# print(end - start)
