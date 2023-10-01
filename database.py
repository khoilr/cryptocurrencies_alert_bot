from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import DB_URL
from models.user import User  # pylint: disable=unused-import

import base  # pylint: disable=unused-import

engine = create_engine(DB_URL)
Session = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)
