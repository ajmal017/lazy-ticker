import re

from typing import List
from datetime import datetime

import pydantic
from pydantic import Field


class Entries(pydantic.BaseModel):
    hashtags: List[str]
    photos: List[str]
    urls: List[str]  # URL?
    videos: List[str]


class TweetSchema(pydantic.BaseModel):
    user_id: int
    tweet_id: int
    published_time: datetime
    symbol: str

    class Config:
        orm_mode = True
        allow_population_by_field_name = True


class ProcessedTweetSchema(pydantic.BaseModel):
    user_id: int
    tweet_id: int
    published_time: datetime
    symbols: List[str] = None

    def process_symbols(self):
        for symbol in self.symbols:
            yield TweetSchema(**self.dict(), symbol=symbol)


class RawTweetSchema(pydantic.BaseModel):
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
        regex_symbol = re.compile(r"\$[^\d\s]\w*")
        matched_symbols = regex_symbol.findall(text)

        if len(matched_symbols) > 0:
            return [cls.clean_symbol(symbol) for symbol in matched_symbols]
        else:
            return None

    def process_raw_tweet(self):
        symbols = self.parse_symbols_from_text(self.text)
        return ProcessedTweetSchema(**self.dict(), symbols=symbols)
