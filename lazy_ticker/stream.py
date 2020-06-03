from tda import auth
from tda.client import Client
from tda.streaming import StreamClient
from paths import PROJECT_ROOT, LOCAL_CHROMEDRIVER_LOCATION
from decouple import config

import asyncio
import json

TOKEN_PATH = PROJECT_ROOT / "token.pickle"
TD_AMERITRADE_API_KEY = config("TD_AMERITRADE_API_KEY")
TD_AMERITRADE_REDIRECT_URI = config("TD_AMERITRADE_REDIRECT_URI")
TD_AMERITRADE_ACCOUNT_NUMBER = config("TD_AMERITRADE_ACCOUNT_NUMBER")
CHROMEDRIVER_LOCATION = config("CHROMEDRIVER_LOCATION", LOCAL_CHROMEDRIVER_LOCATION)
DATABASE_URI = config("DATABASE_URI")

try:
    api = auth.client_from_token_file(TOKEN_PATH, TD_AMERITRADE_API_KEY)
except FileNotFoundError:
    from selenium import webdriver

    with webdriver.Chrome(CHROMEDRIVER_LOCATION) as driver:
        api = auth.client_from_login_flow(
            driver, TD_AMERITRADE_API_KEY, TD_AMERITRADE_REDIRECT_URI, TOKEN_PATH
        )
stream_client = StreamClient(api, account_id=TD_AMERITRADE_ACCOUNT_NUMBER)


SYMBOLS = ["/MES", "/ES", "/GC", "/NQ", "/RTY", "/EMD", "/YM", "/NKD", "/VX", "/BTC"]
ENERGY = ["/QG", "/RB", "/HO", "/CL", "/NG", "/QM", "/BZ"]


from pydantic import BaseModel, validate_arguments
from decimal import Decimal
from datetime import datetime
from typing import List

from sqlalchemy import Column, Integer, BigInteger, String, DateTime, Numeric, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class ChartData(Base):

    __tablename__ = "chartdata"
    id = Column(Integer, index=True, primary_key=True, autoincrement=True)
    seq = Column(BigInteger, nullable=False)
    key = Column(String(length=16), nullable=False)
    CHART_TIME = Column(DateTime)
    OPEN_PRICE = Column(Numeric)
    HIGH_PRICE = Column(Numeric)
    LOW_PRICE = Column(Numeric)
    CLOSE_PRICE = Column(Numeric)
    VOLUME = Column(Numeric)

    __table_args__ = (UniqueConstraint("CHART_TIME", "key"),)


class ChartTick(BaseModel):
    seq: int
    key: str  # "/RB",
    CHART_TIME: datetime  # 1591148220000,
    OPEN_PRICE: Decimal  # 1.1257000000000001,
    HIGH_PRICE: Decimal  # 1.1257000000000001,
    LOW_PRICE: Decimal  # 1.1252,
    CLOSE_PRICE: Decimal  # 1.1252,
    VOLUME: Decimal  # 2.0


class ChartFuturesResponse(BaseModel):
    service: str
    timestamp: datetime
    command: str
    content: List[ChartTick]


from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import exc

engine = create_engine(DATABASE_URI, echo=False)
ChartData.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()


@validate_arguments
def insert(response: ChartFuturesResponse):
    print(response.service)
    print(response.timestamp)
    for candle in response.content:
        record = ChartData(**candle.dict())
        print(".", flush=True, end="")
        try:
            session.add(record)
            session.commit()
        except exc.IntegrityError as e:
            session.rollback()
    else:
        print()


async def read_stream():

    await stream_client.login()
    await stream_client.quality_of_service(StreamClient.QOSLevel.EXPRESS)

    await stream_client.chart_futures_subs(SYMBOLS + ENERGY)
    stream_client.add_chart_futures_handler(lambda msg: insert(msg))

    while True:
        await stream_client.handle_message()


asyncio.get_event_loop().run_until_complete(read_stream())
