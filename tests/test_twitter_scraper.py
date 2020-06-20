import pytest

from lazy_ticker.twitter_scraper import scrape_user_id


def test_scrape_user_id():
    resulted_user_id = scrape_user_id("dgnsrekt")
    expected_user_id = 2474416796
    assert resulted_user_id == expected_user_id
