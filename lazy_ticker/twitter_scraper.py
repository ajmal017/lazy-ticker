import re

from twitter_scraper import get_tweets, Profile
from pydantic import validate_arguments
from typing import Optional
from datetime import datetime

from lazy_ticker.schemas import TwitterUserSchema, TweetSchema
from lazy_ticker.configuration import Configuration

TWITTER_MAX_PAGE_SEARCH = Configuration.TWITTER_MAX_PAGE_SEARCH
TWITTER_MAX_TICKERS_PER_USER = Configuration.TWITTER_MAX_TICKERS_PER_USER


@validate_arguments
def scrape_users_tweets(user: str, break_on_id: Optional[int] = None) -> TweetSchema:
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

            if tickers_found >= TWITTER_MAX_TICKERS_PER_USER:
                break

            else:
                yield tweet


def scrape_user_id(username: str) -> Optional[int]:
    try:
        return int(Profile(username).user_id)
    except IndexError as e:  # TODO rewrite Profile for better error handling.
        return None
