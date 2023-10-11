import uuid
from datetime import datetime

from sqlalchemy import UUID, Column, DateTime, Integer, String

from stream.database import Base


class Crypto(Base):
    __tablename__ = "cryptos"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        index=True,
        default=uuid.uuid4,
    )
    symbol = Column(
        String(20),
        nullable=False,
        index=True,
    )
    base_asset = Column(
        String(10),
        nullable=False,
        index=True,
    )
    quote_asset = Column(
        String(10),
        nullable=False,
        index=True,
    )
    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.now,
    )
    count = Column(Integer, nullable=False)
