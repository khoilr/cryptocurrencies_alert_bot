import uuid

from sqlalchemy import Column, Integer, String
from sqlalchemy.dialects.postgresql import UUID

from stream.database import Base


class Crypto(Base):
    __tablename__ = "cryptos"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    symbol = Column(String(20), nullable=False, index=True)
    base_asset = Column(String(10), nullable=False, index=True)
    quote_asset = Column(String(10), nullable=False, index=True)
    updated_at = Column(Integer, nullable=False, index=True)
    count = Column(Integer, nullable=False, index=True)
