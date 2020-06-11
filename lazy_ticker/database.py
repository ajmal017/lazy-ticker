from contextlib import contextmanager

from pydantic import validate_arguments, PostgresDsn
from typing import List
from .schema import Instrument, Hours
from decouple import config
from . import models
from .models import Base

from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from sqlalchemy import desc

from enum import Enum


class LazyDB:
    DATABASE_URI = config("DATABASE_URI")

    @staticmethod
    @contextmanager
    @validate_arguments
    def connect(postgres_uri: PostgresDsn):
        engine = create_engine(postgres_uri)
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        yield Session

    @classmethod
    def add_symbols(cls, symbols: List[Instrument]) -> None:
        with cls.connect(cls.DATABASE_URI) as Session:
            session = Session()

            for symbol in symbols:
                instrument = models.Instruments(**symbol.dict())
                try:
                    session.add(instrument)
                    session.commit()
                except IntegrityError:
                    session.rollback()
                    query = (
                        session.query(models.Instruments)
                        .filter(models.Instruments.symbol == instrument.symbol)
                        .update({"date": datetime.utcnow()})
                    )
                    session.commit()
                    session.flush()

    @classmethod
    def get_symbols(cls):
        with cls.connect(cls.DATABASE_URI) as Session:
            session = Session()
            query = session.query(models.Instruments)
            instruments = [Instrument.from_orm(q) for q in query]
        return instruments

    @classmethod
    @validate_arguments
    def get_symbols_since(cls, hours: Hours):
        since = datetime.utcnow() - timedelta(hours=hours.value)
        with cls.connect(cls.DATABASE_URI) as Session:
            session = Session()
            query = session.query(models.Instruments).filter(models.Instruments.date > since)
            instruments = [Instrument.from_orm(q) for q in query]
        return instruments

    @classmethod
    def get_most_recent(cls, amount: int):
        with cls.connect(cls.DATABASE_URI) as Session:
            session = Session()
            query = (
                session.query(models.Instruments)
                .order_by(models.Instruments.date.desc())
                .limit(amount)
                .all()
            )
            instruments = [Instrument.from_orm(q) for q in query]
        return instruments
