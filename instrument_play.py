from lazy_ticker.tda_scraper import get_instruments
from string import ascii_uppercase
from random import choices


def get_random_tickers(amount):
    for _ in range(amount):
        yield "".join(choices(ascii_uppercase, k=4))


tickers = []
for ticker in get_random_tickers(1000):
    tickers.append(ticker)


def divide_chunks(container, size):
    for position in range(0, len(container), size):
        yield container[position : position + size]


for chunk in divide_chunks(tickers, 500):
    print(get_instruments(chunk))
