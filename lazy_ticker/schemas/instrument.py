import pydantic
from typing import List, Optional
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
    IND = "IND"
    NYSE = "NYSE"
    NASDAQ = "NASDAQ"
    PACIFIC = "Pacific"
    PINK = "Pink Sheet"
    MUTUAL_FUND = "Mutual Fund"
    UNKOWN = "Unknown"

    def convert_to_tradingview_exchange(self) -> Optional[str]:
        if self is self.PACIFIC:
            return self.AMEX.value
        elif self is self.PINK:
            return "OTC"
        elif self is self.IND:
            return "CBOE"
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

    # TODO: split inverted from normal
    def get_tradingview_ticker(self, inverted: bool = False) -> List[str]:
        exchange = self.exchange.convert_to_tradingview_exchange()
        if exchange:
            ticker = f"{exchange}:{self.symbol}"
        else:
            ticker = f"{self.symbol}"

        if inverted:
            ticker = f"0-{ticker}"
        return ticker


class InstrumentsList(pydantic.BaseModel):
    instruments: List[InstrumentSchema]

    def create_list_tickers(self, *, inverted: bool = False):
        tickers = []
        for ticker in self.instruments:
            tickers.append(ticker.get_tradingview_ticker(inverted=inverted))
        else:
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
