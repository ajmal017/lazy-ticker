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


# TODO: heavy refactoring needed
def prepare_tables_for_watchlist():
    logger.debug("prepare_tables_for_watchlist starts")
    valid_instruments = LazyDB.get_instruments()

    if valid_instruments:
        LazyDB.update_tweet_validation_column(valid_instruments)

    unchecked_symbols = LazyDB.get_all_symbols_from_unchecked_tweets()

    if unchecked_symbols:
        for chunk in divide_chunks(unchecked_symbols, 500):
            valid = get_instruments(chunk).dict()["instruments"]
            LazyDB.add_instruments(valid)

        valid_instruments = LazyDB.get_instruments()
        LazyDB.update_tweet_validation_column(valid_instruments)

    LazyDB.delete_tweets_where_validation_column_is_false()


def restore_users_table_state_from_previous_data():
    # TODO: add config flag
    if DATA_DIRECTORY.exists():
        users = list(set(path.stem for path in DATA_DIRECTORY.glob("**/*.json")))

        for user in users:
            logger.debug(f"restoring {user} from previous state.")
            resp = requests.post(f"http://backend:5001/user/{user}")
            assert resp.status_code == 201


def build_watchlist_table():
    logger.info("building watchlist")
    tweets = LazyDB.get_all_tweets_sorted_by_published_time()
    LazyDB.add_to_watchlist(tweets)
    logger.info("watchlist built")


def start_pipeline(timestamp):
    dt = pendulum.from_timestamp(timestamp, tz="UTC")
    date = dt.date()

    logger.debug("processing", timestamp, dt, dt.timezone_name)

    users = LazyDB.get_all_users()

    if not users:
        logger.info("User table is empty.")
        logger.info("Attempting to restore users table state from previous data")
        restore_users_table_state_from_previous_data()

    # TODO: Add workers to config
    # TODO: WORKERS_PER_CPU config

    twitter_scrape_successful = luigi.build(
        [TwitterScraperPipline(timestamp=timestamp, users=users)], workers=4, local_scheduler=False
    )

    if twitter_scrape_successful:
        prepare_tables_for_watchlist()
        logger.debug("prepare_tables_for_watchlist complete!")
        build_watchlist_table()
    else:
        logger.debug("notification of twitter scraping issue")
        # TODO notification of scraping unsuccesful.

    # clean_data_folder()

    # TODO: clean_up_job(start) remove folders older than start task
    # clean up task is optional. conig option
    # only clean up if all the above tasks were successful and cleanup task setting is trueI
    # clean up data folder date > 24 hours | max days back configuration | older than n days setting


def start_task_loop(*, minute_interval: int):

    logger.debug(f"sleeping for 10 seconds.")

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
                    sleep(1)
                else:
                    start_pipeline(period.int_timestamp)


def wait(seconds):
    for n in range(seconds, 0, -1):
        logger.debug(f"{n}!")
        sleep(1)
    else:
        logger.debug(f"go!")


if __name__ == "__main__":
    wait(10)
    # TODO: Configuration.task_execution_interval
    start_task_loop(minute_interval=1)
