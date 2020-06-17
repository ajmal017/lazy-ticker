import re

from twitter_scraper import get_tweets, Profile
from pydantic import validate_arguments
from typing import Optional
from datetime import datetime

from lazy_ticker.schemas import RawTweetSchema, ProcessedTweetSchema


@validate_arguments
def get_symbols_from_tweets(
    twitter_name: str, max_tickers: int, max_pages: int, break_on_tweet_id=Optional[int]
) -> ProcessedTweetSchema:
    tickers_found = 0

    for tweet in get_tweets(twitter_name, pages=max_pages):
        if tweet["isRetweet"] == True:
            continue

        tweet = RawTweetSchema(**tweet).process_raw_tweet()

        if tweet.tweet_id == break_on_tweet_id:
            break

        if tweet.symbols:

            tickers_found += len(tweet.symbols)
            if tickers_found >= max_tickers:
                break
            else:
                yield tweet


def get_twitter_user_id(username: str) -> int:
    return int(Profile(username).user_id)


#
# tweet_id = 1273041703193112579
# tweet_id = None
# from pprint import pprint as print
#
# for tweet in get_symbols_from_tweets(
#     "seekingalpha", max_tickers=200, max_pages=10, break_on_tweet_id=tweet_id
# ):
#     for s in tweet.process_symbols():
#         print(s.json())
