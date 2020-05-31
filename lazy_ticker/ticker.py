from tda import auth, client
from paths import PROJECT_ROOT
from decouple import config
import json

TOKEN_PATH = PROJECT_ROOT / "token.pickle"
TD_AMERITRADE_API_KEY = config("TD_AMERITRADE_API_KEY")
TD_AMERITRADE_REDIRECT_URI = config("TD_AMERITRADE_REDIRECT_URI")

print(TOKEN_PATH)
print(PROJECT_ROOT)
print(TD_AMERITRADE_API_KEY)
print(TD_AMERITRADE_REDIRECT_URI)

#
# try:
#     c = auth.client_from_token_file(token_path, api_key)
# except FileNotFoundError:
#     from selenium import webdriver
#
#     with webdriver.Chrome() as driver:
#         c = auth.client_from_login_flow(driver, api_key, redirect_uri, token_path)
#
# r = c.get_price_history(
#     "AAPL",
#     period_type=client.Client.PriceHistory.PeriodType.YEAR,
#     period=client.Client.PriceHistory.Period.TWENTY_YEARS,
#     frequency_type=client.Client.PriceHistory.FrequencyType.DAILY,
#     frequency=client.Client.PriceHistory.Frequency.DAILY,
# )
# assert r.ok, r.raise_for_status()
# print(json.dumps(r.json(), indent=4))
