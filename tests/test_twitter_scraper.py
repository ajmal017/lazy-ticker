import pytest

from lazy_ticker.twitter_scraper import get_user_id


def test_get_user_id():
    resulted_user_id = get_user_id("dgnsrekt")
    expected_user_id = 2474416796
    assert resulted_user_id == expected_user_id
