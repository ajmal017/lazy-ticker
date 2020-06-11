from twitter_scraper import get_tweets
import re
from pprint import pprint as print


def clean_ticker(ticker):
    return ticker.replace("$", "")


def parse_tickers_from_text(text):
    tickerTweetRegex = re.compile(r"\$[^\d\s]\w*")
    tweets = tickerTweetRegex.findall(text)
    if len(tweets) > 0:
        return tweets
    else:
        return None


def clean_tweet(tweet):
    tweet.pop("entries")
    tweet.pop("isPinned")
    tweet.pop("likes")
    tweet.pop("replies")
    tweet.pop("retweets")
    tweet.pop("isRetweet")
    tweet.pop("tweetUrl")
    tweet.pop("text")
    return tweet


def get_stocks_from_twitter(twitter_name, max_tickers=9, max_pages=10):

    ticker_count = 0
    group = []

    for tweet in get_tweets(twitter_name, pages=max_pages):  # should be a generator somewhere.

        if tweet["isRetweet"]:
            continue

        symbols = parse_tickers_from_text(tweet["text"])

        if symbols:
            cleaned_tweet = clean_tweet(tweet)
            symbols = list(set([clean_ticker(symbol) for symbol in symbols]))
            ticker_count += len(symbols)

            for symbol in symbols:
                cleaned_tweet["symbol"] = symbol
                group.append(cleaned_tweet.copy())

        if ticker_count >= max_tickers:
            return group

    return group


x = get_stocks_from_twitter("seekingalpha", max_tickers=100)
print(x)
