import luigi
from luigi import LocalTarget, Task, WrapperTask
import pydantic
from lazy_ticker.paths import PROJECT_ROOT
from lazy_ticker.database import LazyDB
from lazy_ticker.schemas import TwitterUserSchemaList, TweetSchemaContainer
from lazy_ticker.twitter_scraper import get_symbols_from_tweets
from pathlib import Path
from time import sleep
import pendulum
from datetime import date
from loguru import logger
import sys
import json

DATA_DIRECTORY = PROJECT_ROOT / "data"

logger.add(sys.stdout, colorize=True, format="<green>{time}</green> <level>{message}</level>")


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


def make_check_directory(target: LocalTarget):
    output_path = convert_to_path(target)
    output_path.mkdir()
    assert output_path.exists()


class MakeDataDirectory(Task):
    def output(self):
        return convert_to_target(DATA_DIRECTORY)

    def run(self):
        make_check_directory(self.output())


class CreateDateDirectory(Task):
    timestamp = luigi.IntParameter()  # add description

    def requires(self):
        return MakeDataDirectory()

    def output(self):
        data_directory = convert_to_path(self.input())
        date_ = pendulum.from_timestamp(self.timestamp).date()
        target_directory = data_directory / convert_date_to_string(date_)
        return convert_to_target(target_directory)

    def run(self):
        make_check_directory(self.output())


class CreateUsersDirectory(Task):
    timestamp = luigi.IntParameter()  # add description

    def requires(self):
        return CreateDateDirectory(self.timestamp)

    def output(self):
        current_date_directory = convert_to_path(self.input())
        target_directory = current_date_directory / "users"
        return convert_to_target(target_directory)

    def run(self):
        make_check_directory(self.output())


class GetUserList(Task):
    timestamp = luigi.IntParameter()  # add description

    def requires(self):
        return CreateUsersDirectory(self.timestamp)

    def output(self):
        current_users_directory = convert_to_path(self.input())
        target_file = current_users_directory / f"{self.timestamp}.json"
        return convert_to_target(target_file)

    def run(self):
        all_users = LazyDB.get_all_users()
        all_users_json = TwitterUserSchemaList.parse_obj(all_users).json()
        output_path = convert_to_path(self.output())

        with open(output_path, mode="w") as user_write_file:
            user_write_file.write(all_users_json)

        assert output_path.exists()


class CreateTweetsDirectory(Task):
    timestamp = luigi.IntParameter()  # add description

    def requires(self):
        return CreateDateDirectory(self.timestamp)

    def output(self):
        current_date_directory = convert_to_path(self.input())
        target_directory = current_date_directory / "tweets"
        return convert_to_target(target_directory)

    def run(self):
        make_check_directory(self.output())


class CreateTimeStampTweetDirectory(Task):
    timestamp = luigi.IntParameter()  # add description

    def requires(self):
        return CreateTweetsDirectory(self.timestamp)

    def output(self):
        current_date_directory = convert_to_path(self.input())
        target_directory = current_date_directory / str(self.timestamp)
        return convert_to_target(target_directory)

    def run(self):
        make_check_directory(self.output())


class GetSingleUserTweets(Task):
    timestamp = luigi.IntParameter()  # add description
    username = luigi.Parameter()

    def requires(self):
        return CreateTimeStampTweetDirectory(self.timestamp)

    def output(self):
        current_date_directory = convert_to_path(self.input())
        target_file = current_date_directory / (self.username + ".json")
        return convert_to_target(target_file)

    def run(self):
        output_path = convert_to_path(self.output())
        tweets_with_symbols = []

        for preprocessed in get_symbols_from_tweets(self.username, max_tickers=100, max_pages=2):
            for tweet in preprocessed.process_symbols():
                tweets_with_symbols.append(tweet)
                logger.debug(tweet)
                logger.debug(type(tweet))

        logger.debug(f"TWEETS WITH SYMBOLS!!! {tweets_with_symbols}")
        container = TweetSchemaContainer(
            __root__=tweets_with_symbols
        )  # NOTE Maybe easier with a json
        logger.debug(f"container!!! {container}")

        with open(output_path, mode="w") as tweet_write_file:
            tweet_write_file.write(container.json())

        assert output_path.exists()


class AddTweetToDatabase(Task):
    timestamp = luigi.IntParameter()  # add description
    username = luigi.Parameter()

    def requires(self):
        return GetSingleUserTweets(timestamp=self.timestamp, username=self.username)

    def complete(self):
        input_path = convert_to_path(self.input())
        if input_path.exists():
            with open(input_path, mode="r") as read_file:
                data = json.load(read_file)

            for tweet in data:
                assert LazyDB.tweet_id_exists(
                    int(tweet["tweet_id"])
                )  # should pass all tweets to function
                # assert int(tweet["tweet_id"]) == int(q.tweet_id)
            else:
                return True

        return False

    def run(self):
        input_path = convert_to_path(self.input())

        with open(input_path, mode="r") as read_file:
            data = json.load(read_file)

        for tweet in data:
            LazyDB.add_tweet(tweet)  # should pass all tweets to function
            logger.debug(f"added {tweet}")


class PiplineWrapper(WrapperTask):
    timestamp = luigi.IntParameter()  # add description

    def requires(self):
        all_users = LazyDB.get_all_users()
        return [
            AddTweetToDatabase(timestamp=self.timestamp, username=user.name) for user in all_users
        ]

        # return [
        #     GetSingleUserTweets(timestamp=self.timestamp, username=user)
        #     for user in ["seekingalpha", "wallstjesus", "no_pullbacks", "dgnsrekt"]
        # ]


from time import sleep
import pendulum

# TODO: LOGGING! LOGURU
def process_job(timestamp):
    dt = pendulum.from_timestamp(timestamp)
    date = dt.date()
    print()
    print("processing job", timestamp, dt, dt.timezone_name)
    print(f"data/{date}/users/{timestamp}.json")

    luigi.build([PiplineWrapper(timestamp=timestamp)], local_scheduler=False)


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
                    # clean_up_job(start) remove folders older than start task


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
