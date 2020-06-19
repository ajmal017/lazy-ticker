from contextlib import contextmanager

from lazy_ticker.models import InstrumentBase, InstrumentsTable
from lazy_ticker.models import TwitterModelBase, TwitterUsersTable, TwitterSymbolsTable

from datetime import datetime, timedelta

from sqlalchemy import create_engine
from sqlalchemy import desc
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

from lazy_ticker.configuration import Configuration


class LazyDB:
    DATABASE_URI = Configuration.get_database_uri()

    @classmethod
    @contextmanager
    def connect(cls):
        engine = create_engine(cls.DATABASE_URI)
        InstrumentBase.metadata.create_all(engine)
        TwitterModelBase.metadata.create_all(engine)

        Session = sessionmaker(bind=engine)
        yield Session

    @classmethod
    def test_database_connection(cls):
        with cls.connect() as Session:
            session = Session()
            session.close()

    @classmethod
    def add_user(cls, name: str, user_id: int):
        with cls.connect() as Session:
            session = Session()
            try:
                twitter_user = TwitterUsersTable(name=name, user_id=user_id)
                session.add(twitter_user)
                session.commit()
                session.close()
                return twitter_user

            except IntegrityError:
                session.rollback()
                session.close()
                return twitter_user

    @classmethod
    def remove_user(cls, name: str):
        with cls.connect() as Session:
            session = Session()
            query = session.query(TwitterUsersTable).filter(TwitterUsersTable.name == name).first()
            if query:
                session.delete(query)
                session.commit()
            session.close()
            return query

    @classmethod
    def get_user(cls, name: str):
        with cls.connect() as Session:
            session = Session()
            return session.query(TwitterUsersTable).filter(TwitterUsersTable.name == name).first()

    @classmethod
    def get_all_users(cls):
        with cls.connect() as Session:
            session = Session()
            return session.query(TwitterUsersTable).order_by("date").all()

    @classmethod
    def add_tweet(cls, tweet: dict):  # should take a list of tweets to keep the same port open
        with cls.connect() as Session:
            session = Session()
            try:
                tweet = TwitterSymbolsTable(**tweet)
                session.add(tweet)
                session.commit()
                session.close()
                return tweet

            except IntegrityError:
                session.rollback()
                session.close()
                return tweet

    @classmethod
    def tweet_id_exists(cls, tweet_id: int):  # should pass list of all ids
        with cls.connect() as Session:
            session = Session()
            return session.query(TwitterSymbolsTable).filter(TwitterSymbolsTable.tweet_id == tweet_id).scalar()

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
