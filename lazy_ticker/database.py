import sys
from contextlib import contextmanager

from lazy_ticker.models import InstrumentBaseModel, InstrumentsTable
from lazy_ticker.models import TwitterModelBase, TwitterUsersTable, TwitterSymbolsTable
from lazy_ticker.models import WatchListModelBase, WatchListTable

from datetime import datetime, timedelta

from sqlalchemy import create_engine
from sqlalchemy import desc
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

from typing import List
from pydantic import validate_arguments

from lazy_ticker.configuration import Configuration

from loguru import logger

import pendulum

DATABASE_URI = Configuration.get_database_uri()


class LazyDB:
    @staticmethod
    def create_session():
        engine = create_engine(DATABASE_URI)
        InstrumentBaseModel.metadata.create_all(engine)
        TwitterModelBase.metadata.create_all(engine)
        WatchListModelBase.metadata.create_all(engine)
        return sessionmaker(bind=engine)

    @classmethod
    @contextmanager
    def session_manager(cls):
        Session = cls.create_session()

        session = Session()
        try:
            yield session
        except:
            session.rollback()
            raise
        finally:
            session.close()

    @classmethod
    def add_user(cls, name: str, user_id: int):
        with cls.session_manager() as session:
            user = TwitterUsersTable(name=name, user_id=user_id)
        try:
            session.add(user)
            session.commit()
        except IntegrityError as e:
            session.rollback()
            logger.debug(e)
            return user

    @classmethod
    def remove_user(cls, name: str):
        with cls.session_manager() as session:
            query = (
                session.query(TwitterUsersTable).filter(TwitterUsersTable.name == name).delete()
            )
            session.commit()
            return query

    @classmethod
    def get_user(cls, name: str):
        with cls.session_manager() as session:
            return (
                session.query(TwitterUsersTable)
                .filter(TwitterUsersTable.name == name)
                .one_or_none()
            )

    @classmethod
    def update_users_last_tweet_column(cls, name: str, last_tweet_id: int):
        with cls.session_manager() as session:
            query = (
                session.query(TwitterUsersTable)
                .filter(TwitterUsersTable.name == name)
                .one_or_none()
            )
            query.last_tweet_id = last_tweet_id
            session.commit()

    @classmethod
    def get_all_users(cls):
        with cls.session_manager() as session:
            return session.query(TwitterUsersTable).order_by("date").all()

    @classmethod
    def add_tweets(cls, tweets: List[dict]):
        with cls.session_manager() as session:
            for tweet in tweets:
                try:
                    tweet = TwitterSymbolsTable(**tweet)
                    session.add(tweet)
                    session.commit()
                except IntegrityError as e:
                    session.rollback()
                    logger.debug(e)

    @classmethod
    @validate_arguments
    def check_all_tweets_exists(cls, tweets: List[dict]):
        with cls.session_manager() as session:
            for tweet in tweets:
                query = session.query(TwitterSymbolsTable.tweet_id).filter(
                    TwitterSymbolsTable.tweet_id == tweet["tweet_id"]
                )
                exists = session.query(query.exists()).scalar()
                if not exists:
                    logger.error(f"{tweet} does not exists in the database.")
                    # NOTE: May need to raise an error here.
                    return False
            else:
                return True

    @classmethod
    def update_tweet_validation_column(cls, valid_symbols: List[str]):
        with cls.session_manager() as session:
            for row in session.query(TwitterSymbolsTable).filter(
                TwitterSymbolsTable.valid == None
            ):
                if row.symbol in valid_symbols:
                    row.valid = True
                else:
                    row.valid = False
                session.commit()

    @classmethod
    def delete_tweets_where_validation_column_is_false(cls):
        with cls.session_manager() as session:
            query = TwitterSymbolsTable.__table__.delete().where(
                TwitterSymbolsTable.valid == False
            )
            session.execute(query)
            session.commit()

    @classmethod
    def get_all_tweets_sorted_by_published_time(cls):
        with cls.session_manager() as session:
            return session.query(TwitterSymbolsTable).order_by("published_time").all()

    @classmethod
    def get_all_symbols_from_unchecked_tweets(cls):
        with cls.session_manager() as session:
            query = (
                session.query(TwitterSymbolsTable).filter(TwitterSymbolsTable.valid == None).all()
            )
            return list(set([symbol.symbol for symbol in query]))

    @classmethod
    def add_instruments(cls, instruments: List[dict]):
        with cls.session_manager() as session:
            for ticker in instruments:
                try:
                    instrument = InstrumentsTable(**ticker)
                    session.add(instrument)
                    session.commit()
                except IntegrityError as e:
                    session.rollback()
                    logger.debug(e)

    @classmethod
    def get_instruments(cls):
        with cls.session_manager() as session:
            return [symbol.symbol for symbol in session.query(InstrumentsTable.symbol)]

    @classmethod
    def add_to_watchlist(cls, tweets: List[TwitterSymbolsTable]):
        with cls.session_manager() as session:
            for tweet in tweets:

                symbol = tweet.symbol
                publish_time = tweet.published_time

                query = (
                    session.query(WatchListTable)
                    .filter(WatchListTable.symbol == symbol)
                    .one_or_none()
                )

                if query:
                    if publish_time > query.time:
                        query.time = publish_time
                        session.commit()
                    else:
                        continue
                else:
                    row = WatchListTable(symbol=symbol, time=publish_time)
                    session.add(row)
                    session.commit()

    @classmethod
    def get_watchlist_symbols_within_time_period(cls, time_period: dict):
        with cls.session_manager() as session:
            filter_period = pendulum.now("UTC").subtract(**time_period)

            query = (
                session.query(WatchListTable)
                .filter(WatchListTable.time > filter_period)
                .order_by(WatchListTable.time.desc())
                .all()
            )

            instruments = []
            for symbol in query:
                current = (
                    session.query(InstrumentsTable)
                    .filter(InstrumentsTable.symbol == symbol.symbol)
                    .one_or_none()
                )
                if current:
                    instruments.append(current)

            return instruments

    @classmethod
    def get_most_recently_tweeted_symbol(cls):
        with cls.session_manager() as session:
            return (
                session.query(TwitterSymbolsTable)
                .order_by(TwitterSymbolsTable.published_time.desc())
                .first()
            )

    @classmethod
    def get_most_recent_unique_ticker(cls):
        with cls.session_manager() as session:
            return session.query(InstrumentsTable).order_by(InstrumentsTable.date.desc()).first()
