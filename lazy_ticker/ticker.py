from tda import auth
from tda.client import Client
from paths import PROJECT_ROOT, LOCAL_CHROMEDRIVER_LOCATION
from decouple import config
import json

TOKEN_PATH = PROJECT_ROOT / "token.pickle"
TD_AMERITRADE_API_KEY = config("TD_AMERITRADE_API_KEY")
TD_AMERITRADE_REDIRECT_URI = config("TD_AMERITRADE_REDIRECT_URI")
CHROMEDRIVER_LOCATION = config("CHROMEDRIVER_LOCATION", LOCAL_CHROMEDRIVER_LOCATION)

try:
    api = auth.client_from_token_file(TOKEN_PATH, TD_AMERITRADE_API_KEY)
except FileNotFoundError:
    from selenium import webdriver

    with webdriver.Chrome(CHROMEDRIVER_LOCATION) as driver:
        api = auth.client_from_login_flow(
            driver, TD_AMERITRADE_API_KEY, TD_AMERITRADE_REDIRECT_URI, TOKEN_PATH
        )

# NOTE: Think about a max chunking

DATABASE = ["AAP"]
search = ["AAPL", "TSLA", "GE", "SPY"]


def filter_database(tickers):
    if not tickers in DATABASE:
        return True
    else:
        return False


search = list(filter(filter_database, search))
# for s in search:
#    print(s)


def verify_ticker(tickers):

    response = api.search_instruments(
        tickers, projection=Client.Instrument.Projection.SYMBOL_SEARCH,
    )

    assert response.ok, response.raise_for_status()
    # print(json.dumps(response.json(), indent=4))
    return response.json()


from pydantic import BaseModel, validator, validate_arguments
from typing import List
from pprint import pprint as print

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
    NYSE = "NYSE"
    NASDAQ = "NASDAQ"
    PACIFIC = "Pacific"


class Instrument(BaseModel):
    cusip: str
    symbol: str
    description: str
    exchange: Exchange
    assetType: AssetType


@validate_arguments
def insert(instrument: Instrument):
    print(instrument)


r = verify_ticker(search)
for entry in r.values():
    insert(entry)
