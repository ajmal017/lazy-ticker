import pydantic
from pydantic import validate_arguments, Field
from typing import List

from enum import Enum


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
    BATS = "BATS"
    NYSE = "NYSE"
    NASDAQ = "NASDAQ"
    PACIFIC = "Pacific"
    PINK = "Pink Sheet"
    UNKOWN = "Unknown"


class Instrument(pydantic.BaseModel):
    cusip: str
    symbol: str
    description: str
    exchange: Exchange
    asset_type: AssetType = Field(alias="assetType")
