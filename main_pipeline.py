from lazy_ticker.pipeline import TwitterScraperPipline
from lazy_ticker.database import LazyDB
from lazy_ticker.paths import DATA_DIRECTORY

import luigi
from time import sleep
from loguru import logger
import pendulum
import requests

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


# TODO: heavy refactoring
def prepare_for_watchlist():
    logger.debug("prepare_for_watchlist starts")
    valid_instruments = LazyDB.get_instruments()

    if valid_instruments:
        LazyDB.update_tweets(valid_instruments)

    uncheck_symbols = LazyDB.get_uncheck_symbols_from_tweets()

    if uncheck_symbols:
        for chunk in divide_chunks(uncheck_symbols, 500):
            valid = get_instruments(chunk).dict()["instruments"]
            LazyDB.add_instruments(valid)

        valid_instruments = LazyDB.get_instruments()
        LazyDB.update_tweets(valid_instruments)

    LazyDB.delete_invalid_tweets()


def restore_usertable_from_previous_states():
    # TODO: add config flag
    if DATA_DIRECTORY.exists():
        users = list(set(path.stem for path in DATA_DIRECTORY.glob("**/*.json")))
        for user in users:
            logger.debug(f"restoring {user} from previous state.")
            # TODO you can animate this
            resp = requests.post(f"http://backend/user/{user}")
            assert resp.status_code == 201


def start_pipeline(timestamp):
    dt = pendulum.from_timestamp(timestamp, tz="UTC")
    date = dt.date()

    logger.debug("processing job", timestamp, dt, dt.timezone_name)
    logger.debug(f"data/{date}/users/{timestamp}.json")

    # TODO: Add workers to config | TODO: dive into luigi config
    users = LazyDB.get_all_users()

    if not users:
        restore_usertable_from_previous_states()

    twitter_scrape_successful = luigi.build(
        [TwitterScraperPipline(timestamp=timestamp, users=users)], workers=3, local_scheduler=False
    )

    if twitter_scrape_successful:
        prepare_for_watchlist()  # better naming
        logger.debug("prepare_for_watchlist complete!")
    else:
        logger.debug("notification of twitter scraping issue")
        # TODO notification of scraping unsuccesful.

    # build watchlist one
    # build watchlist two

    # TODO: clean_up_job(start) remove folders older than start task
    # clean up task is optional. conig option
    # only clean up if all the above tasks were successful and cleanup task setting is true
    # clean up data folder date > 24 hours | max days back configuration | older than n days setting


def task_loop(*, minute_interval: int, sleep_interval: int = 1):

    logger.debug(f"sleeping for 10 seconds.")

    for n in range(10, 0, -1):
        logger.debug(f"{n}!")
        sleep(1)
    else:
        logger.debug(f"go!")

    while True:
        now = pendulum.now("UTC")
        start = now.subtract(minutes=now.minute, seconds=now.second, microseconds=now.microsecond)
        end = pendulum.tomorrow("UTC")

        periods = list(pendulum.period(start, end).range("minutes", minute_interval))

        for period in periods:
            if pendulum.now("UTC") > period:
                continue
            else:
                while pendulum.now("UTC") < period:
                    sleep(sleep_interval)
                else:
                    start_pipeline(period.int_timestamp)


task_loop(minute_interval=1)
