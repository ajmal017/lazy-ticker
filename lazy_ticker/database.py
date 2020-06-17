from contextlib import contextmanager

from lazy_ticker.models import InstrumentBase, InstrumentTable

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

        Session = sessionmaker(bind=engine)
        yield Session

    @classmethod
    def test_database_connection(cls):
        with cls.connect() as Session:
            session = Session()
            print(session)

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
