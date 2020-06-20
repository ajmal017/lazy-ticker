from lazy_ticker.pipeline import TwitterScraperPipline
from lazy_ticker.database import LazyDB
from lazy_ticker.paths import DATA_DIRECTORY

import luigi
from time import sleep
from loguru import logger
import pendulum
import requests


def restore_usertable_from_previous_states():
    # TODO: add config flag return on false
    url = "http://backend/user"
    # NOTE: will have to be set from docker env
    # NOTE: will probably have to add to configuration obj

    if DATA_DIRECTORY.exists():
        users = list(set(path.stem for path in DATA_DIRECTORY.glob("**/*.json")))
        for user in users:
            logger.debug(f"restoring {user} from previous state.")
            resp = requests.post(f"{url}/{user}")
            assert resp.status_code == 201


def start_pipeline(timestamp):
    dt = pendulum.from_timestamp(timestamp, tz="UTC")
    date = dt.date()

    logger.debug("processing job", timestamp, dt, dt.timezone_name)
    logger.debug(f"data/{date}/users/{timestamp}.json")

    # if get_all_users is empty
    # if config says restart from old state
    # than add users from old state

    # TODO: Add workers to config | TODO: dive into luigi config
    users = LazyDB.get_all_users()

    if not users:
        restore_usertable_from_previous_states()

    luigi.build(
        [TwitterScraperPipline(timestamp=timestamp, users=users)], workers=3, local_scheduler=False
    )
    # TODO: pipeline_task_successful =
    # NOTE: look up external tasks
    # validate symbols pipe
    # get all distinct symbols / null valid
    # get all instruments
    # compare.
    # any distinct symbols that are in instruments mark valid = True

    # get all distinct symbols / null valid
    # seach tda to look for valid symbols iter 500 at a time
    # mark rows valid = True

    # mark all other rows valid = False

    # remove any invalid rows

    # build watchlist one
    # build watchlist two


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
                    # TODO: clean_up_job(start) remove folders older than start task
                    # clean up task is optional. conig option
                    # only clean up if all the above tasks were successful and cleanup task setting is true
                    # clean up data folder date > 24 hours | max days back configuration | older than n days setting


task_loop(minute_interval=1)
