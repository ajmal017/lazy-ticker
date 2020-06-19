# from lazy_ticker.database import LazyDB

# from lazy_ticker.schemas import InstrumentSchema
# from lazy_ticker.tda_scraper import *
# from lazy_ticker.twitter_scraper import *
# from lazy_ticker.pipeline import *
#
# LazyDB.test_database_connection()

from time import sleep
import pendulum


def process_job(timestamp):
    dt = pendulum.from_timestamp(timestamp)
    date = dt.date()
    print("processing job", timestamp, dt, dt.timezone_name, dt.date())
    print(f"data/{date}/users/{timestamp}.json")


def start_pipeline_loop(minute_interval, sleep_interval=1):
    while True:
        now = pendulum.now("UTC")
        start = now.subtract(minutes=now.minute, seconds=now.second, microseconds=now.microsecond)
        end = pendulum.tomorrow("UTC")

        periods = list(pendulum.period(start, end).range("minutes", minute_interval))

        for period in periods:
            if pendulum.now() > period:
                print(".", end="", flush=True)
                continue
            else:
                while pendulum.now() < period:
                    print(".", end="", flush=True)
                    sleep(sleep_interval)
                else:
                    process_job(period.int_timestamp)


start_pipeline_loop(1)
