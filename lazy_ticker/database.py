from contextlib import contextmanager

from pydantic import validate_arguments, PostgresDsn

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Base


class LazyDB:
    @staticmethod
    @contextmanager
    @validate_arguments
    def connect(postgres_uri: PostgresDsn):
        engine = create_engine(postgres_uri)
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        yield Session
