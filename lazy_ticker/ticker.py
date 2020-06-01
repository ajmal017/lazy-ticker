from tda import auth
from tda.client import Client
from paths import PROJECT_ROOT, CHROMEDRIVER_LOCATION
from decouple import config
import json

TOKEN_PATH = PROJECT_ROOT / "token.pickle"
TD_AMERITRADE_API_KEY = config("TD_AMERITRADE_API_KEY")
TD_AMERITRADE_REDIRECT_URI = config("TD_AMERITRADE_REDIRECT_URI")

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
for s in search:
    print(s)


def verify_ticker(tickers):

    response = api.search_instruments(
        tickers, projection=Client.Instrument.Projection.SYMBOL_SEARCH,
    )

    assert response.ok, response.raise_for_status()
    print(json.dumps(response.json(), indent=4))


verify_ticker(search)
