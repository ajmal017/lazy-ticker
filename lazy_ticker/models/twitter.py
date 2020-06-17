from sqlalchemy import Column, Integer, String, DateTime, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

TwitterBase = declarative_base()


class TwitterUsersTable(TwitterBase):
    __tablename__ = "twitter_users"

    id = Column(Integer, index=True, primary_key=True, autoincrement=True)
    name = Column(String)
    user_id = Column(BigInteger, index=True)
    date = Column(DateTime, default=datetime.utcnow)
    last_tweet_id = Column(BigInteger, nullable=True)


class TweetsTable(TwitterBase):
    __tablename__ = "tweets"

    id = Column(Integer, index=True, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger)
    tweet_id = Column(BigInteger, unique=True)
    published_time = Column(DateTime)  # Index ?
    symbol = Column(String)
