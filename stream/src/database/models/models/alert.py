from uuid import uuid4

import sqlalchemy as sa
from sqlalchemy.orm import relationship
from database.models.models.crypto_alert_association import crypto_alert_association

from database import Base


class Alert(Base):
    __tablename__ = "alerts"

    # Attributes
    id = sa.Column(sa.UUID, primary_key=True, default=uuid4)
    created_at = sa.Column(sa.DateTime, nullable=False, server_default=sa.func.now())

    """Relationships"""
    # An alert can have many indicators
    indicators = relationship("Indicator", back_populates="alert", cascade="all, delete-orphan")

    # An alert can have many cryptos
    cryptos = relationship(
        "Crypto",
        secondary=crypto_alert_association,
        back_populates="alerts",
    )

    # An alert belongs to a user
    user_id = sa.Column(sa.BigInteger, sa.ForeignKey("users.id"))
    user = relationship("User", back_populates="alerts")
