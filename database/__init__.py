import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

load_dotenv()

POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "123456")
POSTGRES_DB = os.getenv("POSTGRES_DB", "telegram_bot")

DB_URL = f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@\
{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

Base = declarative_base()

from database.models.dto.alert import Alert
from database.models.dto.crypto import Crypto
from database.models.dto.indicator import Indicator
from database.models.dto.user import User
from database.models.dto.param import Param

engine = create_engine(DB_URL)
Session = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)
session = Session()
