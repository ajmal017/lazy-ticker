from tda import auth, client
from paths import PROJECT_ROOT, CHROMEDRIVER_LOCATION
from decouple import config
import json

TOKEN_PATH = PROJECT_ROOT / "token.pickle"
TD_AMERITRADE_API_KEY = config("TD_AMERITRADE_API_KEY")
TD_AMERITRADE_REDIRECT_URI = config("TD_AMERITRADE_REDIRECT_URI")

try:
    c = auth.client_from_token_file(TOKEN_PATH, TD_AMERITRADE_API_KEY)
except FileNotFoundError:
    from selenium import webdriver

    with webdriver.Chrome(CHROMEDRIVER_LOCATION) as driver:
        c = auth.client_from_login_flow(
            driver, TD_AMERITRADE_API_KEY, TD_AMERITRADE_REDIRECT_URI, TOKEN_PATH
        )

r = c.get_price_history(
    "AAPL",
    period_type=client.Client.PriceHistory.PeriodType.YEAR,
    period=client.Client.PriceHistory.Period.TWENTY_YEARS,
    frequency_type=client.Client.PriceHistory.FrequencyType.DAILY,
    frequency=client.Client.PriceHistory.Frequency.DAILY,
)
assert r.ok, r.raise_for_status()
print(json.dumps(r.json(), indent=4))
