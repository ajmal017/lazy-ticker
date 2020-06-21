import sys
from contextlib import contextmanager

from lazy_ticker.models import InstrumentBaseModel, InstrumentsTable
from lazy_ticker.models import TwitterModelBase, TwitterUsersTable, TwitterSymbolsTable

from datetime import datetime, timedelta

from sqlalchemy import create_engine
from sqlalchemy import desc
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

from typing import List
from pydantic import validate_arguments

from lazy_ticker.configuration import Configuration

from loguru import logger

DATABASE_URI = Configuration.get_database_uri()


class LazyDB:
    @staticmethod
    def create_session():
        engine = create_engine(DATABASE_URI)
        InstrumentBaseModel.metadata.create_all(engine)
        TwitterModelBase.metadata.create_all(engine)
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
    def update_users_last_tweet(cls, name: str, last_tweet_id: int):
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
                    return False
            else:
                return True

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
    def get_uncheck_symbols_from_tweets(cls):
        with cls.session_manager() as session:
            query = (
                session.query(TwitterSymbolsTable).filter(TwitterSymbolsTable.valid == None).all()
            )
            return list(set([symbol.symbol for symbol in query]))

    @classmethod
    def update_tweets(cls, valid_symbols):
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
    def delete_invalid_tweets(cls):
        with cls.session_manager() as session:
            delete_query = TwitterSymbolsTable.__table__.delete().where(
                TwitterSymbolsTable.valid == False
            )
            session.execute(delete_query)
            session.commit()

    # @classmethod
    # def tweet_id_exists(cls, tweet_id: int):  # should pass list of all ids
    #     with cls.session_manager() as session:
    #         return (
    #             session.query(TwitterSymbolsTable)
    #             .filter(TwitterSymbolsTable.tweet_id == tweet_id)
    #             .scalar()
    #         )
    #
    # @classmethod
    # def query_tweets_by_date_added(cls, date_added: datetime):
    #     with cls.connect() as Session:
    #         session = Session()
    #         return session.query(TwitterUsersTable).filter(TwitterUsersTable.name == name).first()
    #

    # @classmethod
    # def add_symbols(cls, symbols: List[Instrument]) -> None:
    #     with cls.connect(cls.DATABASE_URI) as Session:
    #         session = Session()
    #
    #         for symbol in symbols:
    #             instrument = models.Instruments(**symbol.dict())
    #             try:
    #                 session.add(instrument)
    #                 session.commit()
    #             except IntegrityError:
    #                 session.rollback()
    #                 query = (
    #                     session.query(models.Instruments)
    #                     .filter(models.Instruments.symbol == instrument.symbol)
    #                     .update({"date": datetime.utcnow()})
    #                 )
    #                 session.commit()
    #                 session.flush()
    #
    # @classmethod
    # def get_symbols(cls):
    #     with cls.connect(cls.DATABASE_URI) as Session:
    #         session = Session()
    #         query = session.query(models.Instruments)
    #         instruments = [Instrument.from_orm(q) for q in query]
    #     return instruments
    #
    # @classmethod
    # @validate_arguments
    # def get_symbols_since(cls, hours: Hours):
    #     since = datetime.utcnow() - timedelta(hours=hours.value)
    #     with cls.connect(cls.DATABASE_URI) as Session:
    #         session = Session()
    #         query = session.query(models.Instruments).filter(models.Instruments.date > since)
    #         instruments = [Instrument.from_orm(q) for q in query]
    #     return instruments
    #
    # @classmethod
    # def get_most_recent(cls, amount: int):
    #     with cls.connect(cls.DATABASE_URI) as Session:
    #         session = Session()
    #         query = (
    #             session.query(models.Instruments)
    #             .order_by(models.Instruments.date.desc())
    #             .limit(amount)
    #             .all()
    #         )
    #         instruments = [Instrument.from_orm(q) for q in query]
    #     return instruments
