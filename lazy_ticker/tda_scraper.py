from tda import auth as tda_authenticator
from tda.client import Client as TDAClient

from lazy_ticker.configuration import Configuration
from lazy_ticker.paths import PROJECT_ROOT, LOCAL_CHROMEDRIVER_LOCATION
from lazy_ticker.schemas import InstrumentSchema, InstrumentsList

from typing import List

import pydantic
from pydantic import validate_arguments
from pydantic.error_wrappers import ValidationError
from loguru import logger


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
def get_instruments(symbols: List[str]) -> InstrumentsList:
    assert len(symbols) <= 500
    api = authenticate_client()

    response = api.search_instruments(
        symbols, projection=TDAClient.Instrument.Projection.SYMBOL_SEARCH,
    )

    assert response.ok, response.raise_for_status()

    json_data = list(response.json().values())

    try:
        instruments = [InstrumentSchema(**data) for data in json_data]
        return InstrumentsList(instruments=instruments)
    except ValidationError as e:
        logger.error(e)
        logger.error(json_data)
        raise e
