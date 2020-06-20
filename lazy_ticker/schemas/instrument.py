import pydantic
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
    AMEX = "AMEX"
    BATS = "BATS"
    NYSE = "NYSE"
    NASDAQ = "NASDAQ"
    PACIFIC = "Pacific"
    PINK = "Pink Sheet"
    UNKOWN = "Unknown"

    def convert_to_tradingview_exchange(self) -> str:
        if self is self.PACIFIC:
            return self.AMEX.value
        elif self is self.PINK:
            return "OTC"
        elif self is self.UNKOWN:
            return None
        else:
            return self.value


class InstrumentSchema(pydantic.BaseModel):
    cusip: str
    symbol: str
    description: str
    exchange: Exchange
    asset_type: AssetType = pydantic.Field(alias="assetType")

    class Config:
        orm_mode = True
        allow_population_by_field_name = True

    def get_tradingview_ticker(self, include_inverted: bool = True) -> List[str]:
        exchange = self.exchange.convert_to_tradingview_exchange()
        if exchange:
            tickers = [f"{exchange}:{self.symbol}"]
            if include_inverted:
                tickers += [f"0-{exchange}:{self.symbol}"]
        else:
            tickers = [f"{self.symbol}"]
            if include_inverted:
                tickers += [f"0-{self.symbol}"]

        return tickers


if __name__ == "__main__":  # TODO Dump for tests.

    apple = InstrumentSchema(
        cusip=1,
        symbol="appl",
        description="apple desc",
        exchange=Exchange.PINK,
        asset_type=AssetType.EQUITY,
    )
    print(apple)
    print(apple.exchange)
    print(apple.get_tradingview_ticker())
