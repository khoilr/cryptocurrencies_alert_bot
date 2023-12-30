from uuid import uuid4

import sqlalchemy as sa
from sqlalchemy.orm import relationship

from database import Base


class Param(Base):
    __tablename__ = "params"

    # Attributes
    id = sa.Column(sa.UUID, primary_key=True, default=lambda: uuid4)
    name = sa.Column(sa.String, nullable=False)
    value = sa.Column(sa.String, nullable=False)
    created_at = sa.Column(sa.DateTime, nullable=False, server_default=sa.func.now())

    """Relationships"""
    # An indicator belongs to an alert
    indicator_id = sa.Column(sa.UUID, sa.ForeignKey("indicators.id"))
    indicator = relationship("Indicator", back_populates="params")
