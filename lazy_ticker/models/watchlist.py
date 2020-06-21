from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

WatchListModelBase = declarative_base()


class WatchListTable(WatchListModelBase):
    __tablename__ = "watchlist"

    id = Column(Integer, index=True, primary_key=True)
    time = Column(DateTime, index=True)  # Index ?
    symbol = Column(String, unique=True)

    def __repr__(self):
        return f"<{self.symbol}:{self.time}>"
