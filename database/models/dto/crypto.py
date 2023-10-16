import uuid

import sqlalchemy as sa
from sqlalchemy.orm import relationship

from database import Base
from database.models.dto.crypto_alert_association import crypto_alert_association


class Crypto(Base):
    __tablename__ = "cryptos"

    # Attributes
    id = sa.Column(sa.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    symbol = sa.Column(sa.String(20), nullable=False, unique=True)
    base_asset = sa.Column(sa.String(10), nullable=False)
    quote_asset = sa.Column(sa.String(10), nullable=False)
    count = sa.Column(sa.Integer, nullable=False)
    created_at = sa.Column(sa.DateTime, nullable=False, server_default=sa.func.now())
    updated_at = sa.Column(sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now())

    """Relationships"""
    # A crypto can have many alerts
    alerts = relationship("Alert", secondary=crypto_alert_association, back_populates="cryptos")
