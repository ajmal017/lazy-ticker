import re

from twitter_scraper import get_tweets, Profile
from pydantic import validate_arguments
from typing import Optional
from datetime import datetime
from time import sleep
from random import random

from lazy_ticker.schemas import TwitterUserSchema, TweetSchema
from lazy_ticker.configuration import Configuration
from loguru import logger

TWITTER_MAX_PAGE_SEARCH = Configuration.TWITTER_MAX_PAGE_SEARCH
TWITTER_MAX_TICKERS_PER_USER = Configuration.TWITTER_MAX_TICKERS_PER_USER

# IDEA: maybe add a global backoff sleep time variable which gets increase
# by one second between pages if a scrape fails.
# should have a max sleep time.
# BUG: ValueError: Oops! Either "dgnsrekt" does not exist or is private.
# IDEA: rewrite the original get_tweets function to add the feature.
@validate_arguments
def scrape_users_tweets(user: str, break_on_id: Optional[int] = None) -> TweetSchema:
    tickers_found = 0

    for index, tweet in enumerate(get_tweets(user, pages=TWITTER_MAX_PAGE_SEARCH)):
        wait_time = random() / 2
        sleep(wait_time)

        if tweet["isRetweet"] == True:
            continue

        logger.debug(f"\ntweet#:{index} sleep:{wait_time} user:{user}.")

        tweet = TweetSchema(**tweet)
        tweet.populate_symbols()

        if tweet.tweet_id == break_on_id:
            break

        if tweet.symbols:
            tickers_found += len(tweet.symbols)

            if tickers_found >= TWITTER_MAX_TICKERS_PER_USER:
                break

            else:
                yield tweet


def scrape_user_id(username: str) -> Optional[int]:
    try:
        return int(Profile(username).user_id)
    except IndexError as e:  # TODO: Rewrite Profile for better error handling.
        return None
