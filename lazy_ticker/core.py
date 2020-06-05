from database import LazyDB
from decouple import config
from ticker import get_instruments
from models import Instruments
from sqlalchemy.exc import IntegrityError
from datetime import datetime

import string
import random


def generate_random_ticker():
    return "".join(random.choices(string.ascii_letters.upper(), k=4))


def generate_tickers(amount):
    return [generate_random_ticker() for x in range(amount)]


DATABASE_URI = config("DATABASE_URI")
instruments = generate_tickers(500)

r = get_instruments(instruments)

with LazyDB.connect(DATABASE_URI) as Session:
    session = Session()

    for i in r:
        print(i.symbol)
        content = Instruments(**i.dict())
        try:
            session.add(content)
            session.commit()
        except IntegrityError:
            session.rollback()
            q = (
                session.query(Instruments)
                .filter(Instruments.symbol == i.symbol)
                .update({"date": datetime.utcnow()})
            )
            session.commit()
            session.flush()

print("done")
