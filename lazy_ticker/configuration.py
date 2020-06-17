from decouple import config
from pydantic import validate_arguments, PostgresDsn
from lazy_ticker.paths import LOCAL_CHROMEDRIVER_LOCATION


class Configuration:
    DEBUG = config("DEBUG", cast=bool, default=False)

    DATABASE_IP = config("DATABASE_IP")
    DATABASE_PORT = config("DATABASE_PORT")
    DATABASE_USER = config("DATABASE_USER")
    DATABASE_PASSWORD = config("DATABASE_PASSWORD")
    DATABASE_NAME = config("DATABASE_NAME", default="lazydb")
    DATABASE_URI = f"postgresql://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_IP}:{DATABASE_PORT}/{DATABASE_NAME}"

    TD_AMERITRADE_API_KEY = config("TD_AMERITRADE_API_KEY")
    TD_AMERITRADE_REDIRECT_URI = config("TD_AMERITRADE_REDIRECT_URI")
    TD_AMERITRADE_ACCOUNT_NUMBER = config("TD_AMERITRADE_ACCOUNT_NUMBER")

    CHROMEDRIVER_LOCATION = config("CHROMEDRIVER_LOCATION", LOCAL_CHROMEDRIVER_LOCATION)

    @classmethod
    def get_database_uri(cls):
        return cls.check_database_uri(cls.DATABASE_URI)

    @staticmethod
    @validate_arguments
    def check_database_uri(postgres_dsn: PostgresDsn):
        return postgres_dsn
