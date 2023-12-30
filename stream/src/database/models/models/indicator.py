from uuid import uuid4

import sqlalchemy as sa
from sqlalchemy.orm import relationship

from database import Base


class Indicator(Base):
    __tablename__ = "indicators"

    # Attributes
    id = sa.Column(sa.UUID, primary_key=True, default=uuid4)
    name = sa.Column(sa.String, nullable=False)
    condition = sa.Column(sa.String, nullable=False)
    value = sa.Column(sa.String, nullable=False)
    is_active = sa.Column(sa.Boolean, nullable=False, default=True)
    interval = sa.Column(sa.String, nullable=True)
    klines = sa.Column(sa.Integer, nullable=True)
    created_at = sa.Column(sa.DateTime, nullable=False, server_default=sa.func.now())

    """Relationships"""
    # An indicator belongs to an alert
    alert_id = sa.Column(sa.UUID, sa.ForeignKey("alerts.id"))
    alert = relationship("Alert", back_populates="indicators")

    # An indicator can have many params
    params = relationship("Param", back_populates="indicator", cascade="all, delete-orphan")
