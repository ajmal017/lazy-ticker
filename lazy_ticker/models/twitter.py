from sqlalchemy import Column, Integer, String, DateTime, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

TwitterModelBase = declarative_base()


class TwitterUsersTable(TwitterModelBase):
    __tablename__ = "twitter_users"

    id = Column(Integer, index=True, primary_key=True)
    name = Column(String, unique=True)
    user_id = Column(BigInteger, index=True, unique=True)
    date = Column(DateTime, default=datetime.utcnow)
    last_tweet_id = Column(BigInteger, nullable=True, unique=True)

    def __repr__(self):
        return f"<{self.name}>"


class TwitterSymbolsTable(TwitterModelBase):
    __tablename__ = "twitter_symbols"

    id = Column(Integer, index=True, primary_key=True)
    user_id = Column(BigInteger)
    tweet_id = Column(BigInteger, unique=True)
    published_time = Column(DateTime)  # Index ?
    symbol = Column(String)

    def __repr__(self):
        return f"<{self.user_id}:{self.tweet_id}>"
