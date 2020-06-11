import pydantic
from pydantic import validate_arguments, Field
from typing import List

from enum import Enum, IntEnum


class AssetType(str, Enum):
    EQUITY = "EQUITY"
    ETF = "ETF"
    FOREX = "FOREX"
    FUTURE = "FUTURE"
    FUTURE_OPTION = "FUTURE_OPTION"
    INDEX = "INDEX"
    INDICATOR = "INDICATOR"
    MUTUAL_FUND = "MUTUAL_FUND"
    OPTION = "OPTION"
    UNKNOWN = "UNKNOWN"


class Exchange(str, Enum):
    AMEX = "AMEX"
    BATS = "BATS"
    NYSE = "NYSE"
    NASDAQ = "NASDAQ"
    PACIFIC = "Pacific"
    PINK = "Pink Sheet"
    UNKOWN = "Unknown"

    @property
    def tradingview_conversion(self) -> str:
        if self is self.PACIFIC:
            return self.AMEX.value
        elif self is self.PINK:
            return "OTC"
        elif self is self.UNKOWN:
            return None
        else:
            return self.value


class Instrument(pydantic.BaseModel):
    cusip: str
    symbol: str
    description: str
    exchange: Exchange
    asset_type: AssetType = Field(alias="assetType")

    class Config:
        orm_mode = True
        allow_population_by_field_name = True

    def get_trading_view_string(self, include_inverted: bool = False) -> List[str]:
        if self.exchange.tradingview_conversion:
            tv_string = [f"{self.exchange.tradingview_conversion}:{self.symbol}"]
            if include_inverted:
                tv_string += [f"0-{self.exchange.tradingview_conversion}:{self.symbol}"]
        else:
            tv_string = [f"{self.symbol}"]
            if include_inverted:
                tv_string += [f"0-{self.symbol}"]

        return tv_string


class Hours(IntEnum):
    one = 1
    two = 2
    six = 6
    twelve = 12
    twenty_four = 24
