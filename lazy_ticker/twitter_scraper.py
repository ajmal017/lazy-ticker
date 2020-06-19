import re

from twitter_scraper import get_tweets, Profile
from pydantic import validate_arguments
from typing import Optional
from datetime import datetime

from lazy_ticker.schemas import TwitterUserSchema, TweetSchema
from lazy_ticker.configuration import Configuration

TWITTER_MAX_PAGE_SEARCH = Configuration.TWITTER_MAX_PAGE_SEARCH


@validate_arguments
def scrape_users_tweets(user: str, max_tickers: int, break_on_id=Optional[int]) -> TweetSchema:
    tickers_found = 0

    for tweet in get_tweets(user, pages=TWITTER_MAX_PAGE_SEARCH):
        if tweet["isRetweet"] == True:
            continue

        tweet = TweetSchema(**tweet)
        tweet.populate_symbols()

        if tweet.tweet_id == break_on_id:
            break

        if tweet.symbols:
            tickers_found += len(tweet.symbols)

            if tickers_found >= max_tickers:
                break

            else:
                yield tweet


#
def get_user_id(username: str) -> int:
    try:
        return int(Profile(username).user_id)
    except IndexError as e:  # TODO rewrite Profile for better error handling.
        return None
