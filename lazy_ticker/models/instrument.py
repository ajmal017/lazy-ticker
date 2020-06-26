from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

InstrumentBaseModel = declarative_base()


class InstrumentsTable(InstrumentBaseModel):
    """
    Stores basic information about the instrument.
    """

    __tablename__ = "instruments"

    id = Column(Integer, index=True, primary_key=True)
    cusip = Column(String, nullable=True)
    symbol = Column(String, unique=True)
    description = Column(String)
    exchange = Column(String, index=True)
    asset_type = Column(String, index=True)
    date = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<{self.symbol}>"
