import luigi
from luigi import LocalTarget, Task, WrapperTask
import pydantic
from lazy_ticker.paths import DATA_DIRECTORY
from lazy_ticker.schemas import TwitterSymbolList
from lazy_ticker.database import LazyDB
from lazy_ticker.twitter_scraper import scrape_users_tweets
from pathlib import Path
from time import sleep
import pendulum
from datetime import date
from loguru import logger
import sys
import json


@pydantic.validate_arguments
def convert_date_to_string(date: date):
    underscore_string = str(date).replace("-", "_")
    return underscore_string


@pydantic.validate_arguments
def convert_to_target(path: Path):
    return luigi.LocalTarget(str(path))


def convert_to_path(target: LocalTarget):
    if not isinstance(target, LocalTarget):
        raise TypeError(f"Must be type a LocalTarget not {type(target)}")
    return Path(target.path)


def make_check_directory(target: LocalTarget, parents: bool = False):
    output_path = convert_to_path(target)
    output_path.mkdir(parents=parents)
    assert output_path.exists()


def input_path_target_output(input_target: LocalTarget, path: str):  # TODO FIND BETTER NAME
    input_path = convert_to_path(input_target)
    target_path = input_path / path
    return convert_to_target(target_path)


class MakeDateDirectory(Task):
    timestamp = luigi.IntParameter()  # add description

    def output(self):
        processing_date = pendulum.from_timestamp(self.timestamp).date()
        target_directory = DATA_DIRECTORY / convert_date_to_string(processing_date)
        return convert_to_target(target_directory)

    def run(self):
        make_check_directory(self.output(), parents=True)


class CreateTweetsDirectory(Task):
    timestamp = luigi.IntParameter()  # add description

    def requires(self):
        return MakeDateDirectory(self.timestamp)

    def output(self):
        return input_path_target_output(self.input(), "tweets")

    def run(self):
        make_check_directory(self.output())


class CreateTimeStampTweetDirectory(Task):
    timestamp = luigi.IntParameter()  # add description

    def requires(self):
        return CreateTweetsDirectory(self.timestamp)

    def output(self):
        target_path = str(self.timestamp)
        return input_path_target_output(self.input(), target_path)

    def run(self):
        make_check_directory(self.output())


class GetSingleUserTweets(Task):
    timestamp = luigi.IntParameter()  # add description
    user = luigi.Parameter()  # should be user obj

    def requires(self):
        return CreateTimeStampTweetDirectory(self.timestamp)

    def output(self):
        target_file = self.user.name + ".json"
        return input_path_target_output(self.input(), target_file)

    def run(self):
        output_path = convert_to_path(self.output())
        break_id = self.user.last_tweet_id  # NOTE: Dont forget to insert last tweet in the end

        scraped_tweets = []
        for tweet in scrape_users_tweets(self.user.name, break_on_id=break_id):
            scraped_tweets += tweet.get_tweet_symbols()

        symbols = TwitterSymbolList(tweets=scraped_tweets)
        #
        with open(output_path, mode="w") as tweet_write_file:
            tweet_write_file.write(symbols.json())

        assert output_path.exists()


class AddTweetToDatabase(Task):
    timestamp = luigi.IntParameter()  # add description
    user = luigi.Parameter()

    def requires(self):
        return GetSingleUserTweets(timestamp=self.timestamp, user=self.user)

    def complete(self):
        input_path = convert_to_path(self.input())
        logger.debug(f"{self.user} | checking complete.")
        if input_path.exists():
            with open(input_path, mode="r") as read_file:
                tweets = json.load(read_file)["tweets"]

            if len(tweets) < 1:  # NOTE Maybe and is empty method
                return True

            if LazyDB.check_all_tweets_exists(tweets):
                return True

        return False

    def run(self):
        input_path = convert_to_path(self.input())

        with open(input_path, mode="r") as read_file:
            tweets = json.load(read_file)["tweets"]

        logger.info(f"Found {len(tweets)} new tickers from @{self.user.name}.")

        LazyDB.add_tweets(tweets)

        if len(tweets) > 0:  # NOTE: Maybe an is empty method
            tweet_id = tweets[0]["tweet_id"]
            LazyDB.update_users_last_tweet(name=self.user.name, last_tweet_id=tweet_id)


class PiplineWrapper(WrapperTask):
    timestamp = luigi.IntParameter()  # add description

    def requires(self):
        users = LazyDB.get_all_users()
        return [AddTweetToDatabase(timestamp=self.timestamp, user=user) for user in users]


from time import sleep
import pendulum

# TODO: LOGGING! LOGURU
def process_job(timestamp):
    dt = pendulum.from_timestamp(timestamp)
    date = dt.date()
    print()
    print("processing job", timestamp, dt, dt.timezone_name)
    print(f"data/{date}/users/{timestamp}.json")

    luigi.build([PiplineWrapper(timestamp=timestamp)], workers=3, local_scheduler=False)
    # TODO: Add workers to config


def start_pipeline_loop(*, minute_interval: int, sleep_interval: int = 1):

    while True:
        now = pendulum.now("UTC")
        start = now.subtract(minutes=now.minute, seconds=now.second, microseconds=now.microsecond)
        end = pendulum.tomorrow("UTC")

        periods = list(pendulum.period(start, end).range("minutes", minute_interval))

        for period in periods:
            if pendulum.now() > period:
                continue
            else:
                while pendulum.now() < period:
                    sleep(sleep_interval)
                else:
                    process_job(period.int_timestamp)
                    # TODO: clean_up_job(start) remove folders older than start task


def wait():
    logger.debug("waiting")
    for _ in range(5):
        sleep(1)


# from multiprocessing import Process
# p2 = Process(target=start_pipeline_loop, args=(1,))
# p2.start()
# p2.join()
#
wait()
start_pipeline_loop(minute_interval=1)
