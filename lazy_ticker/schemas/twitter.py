import re

from typing import List, Optional
from datetime import datetime

import pydantic
from pydantic import Field


class TwitterUserSchema(pydantic.BaseModel):
    id: int
    name: str
    user_id: int
    date: datetime
    last_tweet_id: Optional[int]

    class Config:
        orm_mode = True
        allow_population_by_field_name = True  # NOTE: IS THIS NEEDED?


class TwitterSymbolSchema(pydantic.BaseModel):
    user_id: int
    tweet_id: int
    published_time: datetime
    symbol: str

    class Config:
        orm_mode = True
        allow_population_by_field_name = True  # NOTE: IS THIS NEEDED?


class TweetSchema(pydantic.BaseModel):
    text: str
    published_time: datetime = Field(alias="time")
    tweet_id: int = Field(alias="tweetId")
    user_id: int = Field(alias="userId")
    username: str
    symbols: List[str] = []

    @staticmethod
    def clean_symbol(ticker):
        return ticker.replace("$", "")

    @classmethod
    def parse_symbols_from_text(cls, text) -> List[str]:
        regex_symbol = re.compile(r"\$[^\d\s]\w*")
        matched_symbols = regex_symbol.findall(text)

        if len(matched_symbols) > 0:
            return [cls.clean_symbol(symbol) for symbol in matched_symbols]
        else:
            return []

    def populate_symbols(self):
        self.symbols = self.parse_symbols_from_text(self.text)

    def get_tweet_symbols(self):
        for symbol in self.symbols:
            yield TwitterSymbolSchema(**self.dict(), symbol=symbol)
