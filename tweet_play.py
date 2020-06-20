from lazy_ticker.models import TwitterUsersTable, TwitterSymbolsTable
from lazy_ticker.schemas import (
    TwitterUserSchema,
    TwitterSymbolSchema,
    TwitterSymbolList,
    TweetSchema,
)
from lazy_ticker.twitter_scraper import scrape_users_tweets, scrape_user_id
from lazy_ticker.database import LazyDB

import pydantic
from typing import List

#
# #
# x = scrape_user_id("dgnsrek")
# print(x)
from pathlib import Path
import json

#
# input_path = Path("data/2020_06_19/tweets/1592525820/seekingalpha.json")
# print(input_path)
# print(input_path.exists())
#
# with open(input_path, mode="r") as read_file:
#     tweets_from_file = json.load(read_file)  # list of dictionaries
#     # tweets_from_file = pydantic.parse_obj_as(List[TwitterSymbolSchema], tweets_from_file)
#
# from pprint import pprint as print
#
# print(tweets_from_file)
# print(type(tweets_from_file))
# print(type(tweets_from_file))
# exists = LazyDB.check_all_tweets_exists(tweets_from_file)
# print(exists)
#
# for tweet in tweets_from_file:
#     print(tweet["tweet_id"])
#

# tweet_id = 1273041703193112579
tweet_id = None
from pprint import pprint as print


scraped_tweets = []
for tweet in scrape_users_tweets("seekingalpha", max_tickers=10, break_on_id=tweet_id):
    scraped_tweets += tweet.get_twitter_symbols()

print(TwitterSymbolList(tweets=scraped_tweets).json())

for user in LazyDB.get_all_users():
    print(user.last_tweet_id)
    print(user.name)
    print(user)
