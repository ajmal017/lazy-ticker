from sqlalchemy import Column, Integer, BigInteger, String, DateTime, Numeric, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class Instruments(Base):
    """
    Stores basic instrument information.
    """

    __tablename__ = "instruments"

    id = Column(Integer, index=True, primary_key=True, autoincrement=True)
    cusip = Column(String, unique=True)
    symbol = Column(String, unique=True, index=True)
    description = Column(String, unique=True)
    exchange = Column(String)
    asset_type = Column(String)
    date = Column(DateTime, default=datetime.utcnow)
