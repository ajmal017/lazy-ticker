from tda import auth
from tda.client import Client
from .paths import PROJECT_ROOT, LOCAL_CHROMEDRIVER_LOCATION
from decouple import config
from .schema import Instrument
from typing import List
from pydantic import validate_arguments
from pydantic.error_wrappers import ValidationError

TOKEN_PATH = PROJECT_ROOT / "token.pickle"
TD_AMERITRADE_API_KEY = config("TD_AMERITRADE_API_KEY")
TD_AMERITRADE_REDIRECT_URI = config("TD_AMERITRADE_REDIRECT_URI")
CHROMEDRIVER_LOCATION = config("CHROMEDRIVER_LOCATION", LOCAL_CHROMEDRIVER_LOCATION)


def authenticate_client():
    try:
        api = auth.client_from_token_file(TOKEN_PATH, TD_AMERITRADE_API_KEY)

    except FileNotFoundError:
        from selenium import webdriver

        with webdriver.Chrome(CHROMEDRIVER_LOCATION) as driver:
            api = auth.client_from_login_flow(
                driver, TD_AMERITRADE_API_KEY, TD_AMERITRADE_REDIRECT_URI, TOKEN_PATH
            )
    finally:
        return api


@validate_arguments
def get_instruments(symbols: List[str]) -> List[Instrument]:
    # MAX TICKERS 500 add max len validation
    api = authenticate_client()

    response = api.search_instruments(
        symbols, projection=Client.Instrument.Projection.SYMBOL_SEARCH,
    )

    assert response.ok, response.raise_for_status()
    json = response.json()
    try:
        return [Instrument(**value) for value in json.values()]
    except ValidationError as e:
        for v in json.values():
            print()
            print(v)
        raise e


if __name__ == "__main__":
    results = get_instruments(["TSLA", "AAPL"])
    print(results)
