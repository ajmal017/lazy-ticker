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
def convert_date_to_string(date: date) -> str:
    underscored_string = str(date).replace("-", "_")
    return underscored_string


@pydantic.validate_arguments
def convert_to_target(path: Path) -> LocalTarget:
    return LocalTarget(str(path))


def convert_to_path(target: LocalTarget) -> Path:
    if not isinstance(target, LocalTarget):
        raise TypeError(f"Target arg must be type LocalTarget not {type(target)}")
    return Path(target.path)


def make_directory_check_exists(target: LocalTarget, parents: bool = False) -> None:
    output_path = convert_to_path(target)
    output_path.mkdir(parents=parents)
    assert output_path.exists()
    return None


def concatenate_targetpath(input_target: LocalTarget, path: str) -> LocalTarget:
    input_path = convert_to_path(input_target)
    target_path = input_path / path
    return convert_to_target(target_path)


class MakeDateDirectory(Task):
    timestamp = luigi.IntParameter()

    def output(self):
        date_processed = pendulum.from_timestamp(self.timestamp, tz="UTC").date()
        target_directory_path = DATA_DIRECTORY / convert_date_to_string(date_processed)
        return convert_to_target(target_directory_path)

    def run(self):
        make_directory_check_exists(self.output(), parents=True)


class MakeTweetsDirectory(Task):
    timestamp = luigi.IntParameter()

    def requires(self):
        return MakeDateDirectory(self.timestamp)

    def output(self):
        return concatenate_targetpath(self.input(), "tweets")

    def run(self):
        make_directory_check_exists(self.output())


class MakeTimeStampDirectory(Task):
    timestamp = luigi.IntParameter()

    def requires(self):
        return MakeTweetsDirectory(self.timestamp)

    def output(self):
        target_directory_path = str(self.timestamp)
        return concatenate_targetpath(self.input(), target_directory_path)

    def run(self):
        make_directory_check_exists(self.output())


class ScrapeUsersTweets(Task):
    timestamp = luigi.IntParameter()
    user = luigi.Parameter()

    def requires(self):
        return MakeTimeStampDirectory(self.timestamp)

    def output(self):
        target_filename = self.user.name + ".json"
        return concatenate_targetpath(self.input(), target_filename)

    def run(self):
        output_path = convert_to_path(self.output())
        break_on_id = self.user.last_tweet_id

        scraped_tweets = []
        for tweet in scrape_users_tweets(self.user.name, break_on_id=break_on_id):
            scraped_tweets += tweet.get_twitter_symbols()

        symbols = TwitterSymbolList(tweets=scraped_tweets)

        with open(output_path, mode="w") as write_file:
            write_file.write(symbols.json())

        assert output_path.exists()


class InsertTweetsInToDatabase(Task):
    timestamp = luigi.IntParameter()
    user = luigi.Parameter()

    def requires(self):
        return ScrapeUsersTweets(timestamp=self.timestamp, user=self.user)

    def complete(self):
        input_path = convert_to_path(self.input())
        logger.debug(f"{self.user} | checking if complete.")
        if input_path.exists():
            with open(input_path, mode="r") as read_file:
                tweets = json.load(read_file)["tweets"]

            if len(tweets) < 1:
                return True

            if LazyDB.check_all_tweets_exists(tweets):
                tweet_id = tweets[0]["tweet_id"]
                LazyDB.update_users_last_tweet(name=self.user.name, last_tweet_id=tweet_id)
                return True

        return False

    def run(self):
        input_path = convert_to_path(self.input())

        with open(input_path, mode="r") as read_file:
            tweets = json.load(read_file)["tweets"]

        logger.info(f"Found {len(tweets)} new tickers from @{self.user.name}.")

        LazyDB.add_tweets(tweets)


class TwitterScraperPipline(WrapperTask):
    timestamp = luigi.IntParameter()
    users = luigi.Parameter()

    def requires(self):
        return [
            InsertTweetsInToDatabase(timestamp=self.timestamp, user=user) for user in self.users
        ]
