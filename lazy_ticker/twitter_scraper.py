import re

from twitter_scraper import get_tweets
import pydantic
from pydantic import Field
from typing import List
from datetime import datetime


class Entries(pydantic.BaseModel):
    hashtags: List[str]
    photos: List[str]
    urls: List[str]  # URL?
    videos: List[str]


class TweetSchema(pydantic.BaseModel):
    entries: Entries
    is_pinned: bool = Field(alias="isPinned")
    is_retweet: bool = Field(alias="isRetweet")
    likes: int
    replies: int
    retweets: int
    text: str
    published_time: datetime = Field(alias="time")
    tweet_id: int = Field(alias="tweetId")
    tweet_url: str = Field(alias="tweetUrl")
    user_id: int = Field(alias="userId")
    username: str

    @staticmethod
    def clean_symbol(ticker):
        return ticker.replace("$", "")

    @classmethod
    def parse_symbols_from_text(cls, text):
        symbol_regex = re.compile(r"\$[^\d\s]\w*")
        matched_symbols = symbol_regex.findall(text)

        if len(matched_symbols) > 0:
            return [cls.clean_symbol(symbol) for symbol in matched_symbols]

        else:
            return None

    def process_tweet(self):
        symbols = self.parse_symbols_from_text(self.text)
        return ProcessedTweetSchema(**self.dict(), symbols=symbols)


class ProcessedTweetSchema(pydantic.BaseModel):
    user_id: int
    tweet_id: int
    published_time: datetime
    symbols: List[str] = None  # start none


def get_stocks_from_twitter(
    twitter_name: int, max_tickers: int, max_pages: int, break_on_tweet_id=None
):
    tickers_found = 0

    for tweet in get_tweets(twitter_name, pages=max_pages):
        if tweet["isRetweet"] == True:
            continue

        tweet = TweetSchema(**tweet).process_tweet()

        if tweet.tweet_id == break_on_tweet_id:
            break

        if tweet.symbols:
            tickers_found += len(tweet.symbols)
            if tickers_found >= max_tickers:
                break
            else:
                yield tweet


id = 1273041703193112579

for idx, x in enumerate(get_stocks_from_twitter("seekingalpha", max_tickers=50, max_pages=5)):
    print(idx)
    print(x)
