import pytest

from lazy_ticker.tda_scraper import authenticate_client, get_instruments


def test_import():
    assert True


@pytest.mark.webtest
def test_get_instruments():
    symbols = ["AAPL", "TSLA"]
    instruments = get_instruments(symbols)
    for i, s in zip(instruments, symbols):
        assert i.symbol == s
