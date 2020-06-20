from tda import auth as tda_authenticator
from tda.client import Client as TDAClient

from lazy_ticker.configuration import Configuration
from lazy_ticker.paths import PROJECT_ROOT, LOCAL_CHROMEDRIVER_LOCATION
from lazy_ticker.schemas import InstrumentSchema

from typing import List

import pydantic
from pydantic import validate_arguments
from pydantic.error_wrappers import ValidationError


TOKEN_PATH = PROJECT_ROOT / "token.pickle"


def authenticate_client():
    try:
        tda_api = tda_authenticator.client_from_token_file(
            TOKEN_PATH, Configuration.TD_AMERITRADE_API_KEY
        )

    except FileNotFoundError:
        from selenium import webdriver

        with webdriver.Chrome(Configuration.CHROMEDRIVER_LOCATION) as driver:
            tda_api = tda_authenticator.client_from_login_flow(
                driver,
                Configuration.TD_AMERITRADE_API_KEY,
                Configuration.TD_AMERITRADE_REDIRECT_URI,
                TOKEN_PATH,
            )
    finally:
        return tda_api


@validate_arguments
def get_instruments(symbols: List[str]) -> List[InstrumentSchema]:
    assert len(symbols) <= 500
    api = authenticate_client()

    response = api.search_instruments(
        symbols, projection=TDAClient.Instrument.Projection.SYMBOL_SEARCH,
    )

    assert response.ok, response.raise_for_status()

    data = list(response.json().values())

    return pydantic.parse_obj_as(List[InstrumentSchema], data)
