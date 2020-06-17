from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

InstrumentBase = declarative_base()


class InstrumentTable(InstrumentBase):
    """
    Stores basic information about the instrument.
    """

    __tablename__ = "instrument"

    id = Column(Integer, index=True, primary_key=True, autoincrement=True)
    cusip = Column(String, unique=True)
    symbol = Column(String, unique=True)
    description = Column(String, unique=True)
    exchange = Column(String)
    asset_type = Column(String)
    date = Column(DateTime, default=datetime.utcnow)
