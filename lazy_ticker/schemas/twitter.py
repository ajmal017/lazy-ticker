import re

from typing import List, Optional
from datetime import datetime

import pydantic


class TwitterUserSchema(pydantic.BaseModel):
    id: int
    name: str
    user_id: int
    date: datetime
    last_tweet_id: Optional[int]

    class Config:
        orm_mode = True


class TwitterSymbolSchema(pydantic.BaseModel):
    user_id: int
    tweet_id: int
    published_time: datetime
    symbol: str

    class Config:
        orm_mode = True


class TwitterSymbolList(pydantic.BaseModel):
    tweets: List[TwitterSymbolSchema]


class TweetSchema(pydantic.BaseModel):
    text: str
    published_time: datetime = pydantic.Field(alias="time")
    tweet_id: int = pydantic.Field(alias="tweetId")
    user_id: int = pydantic.Field(alias="userId")
    username: str
    symbols: List[str] = []

    @staticmethod
    def clean_symbol(ticker: str) -> str:
        regex = re.compile("[^a-zA-Z]")
        return regex.sub("", ticker)

    @classmethod
    def parse_symbols_from_text(cls, text) -> List[str]:  # NOTE: Optional?
        regex_symbol = re.compile(r"\$[^\d\s]\w*")
        matched_symbols = regex_symbol.findall(text)

        if len(matched_symbols) > 0:
            return list(set([cls.clean_symbol(symbol) for symbol in matched_symbols]))
        else:
            return []

    def populate_symbols(self) -> None:
        self.symbols = self.parse_symbols_from_text(self.text)

    def get_twitter_symbols(self) -> List[TwitterSymbolSchema]:
        return [
            TwitterSymbolSchema(**self.dict(), symbol=symbol.upper()) for symbol in self.symbols
        ]

    def __repr__(self):
        return f"<{self.__class__.__name__} id={self.tweet_id}>"
