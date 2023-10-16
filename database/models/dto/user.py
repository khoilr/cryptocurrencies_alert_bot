import sqlalchemy as sa
from sqlalchemy.orm import relationship

from database import Base


class User(Base):
    __tablename__ = "users"

    # Attributes
    id = sa.Column(sa.BigInteger, primary_key=True)
    is_bot = sa.Column(sa.Boolean, nullable=False, default=False)
    first_name = sa.Column(sa.String, nullable=False)
    last_name = sa.Column(sa.String)
    username = sa.Column(sa.String)
    language_code = sa.Column(sa.String)
    is_premium = sa.Column(sa.Boolean, nullable=False, default=False)
    created_at = sa.Column(sa.DateTime, nullable=False, server_default=sa.func.now())
    updated_at = sa.Column(sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now())
    is_upgraded = sa.Column(sa.Boolean, nullable=False, default=False)

    """Relationships"""
    # A user can have many alerts
    alerts = relationship(
        "Alert",
        back_populates="user",
        cascade="all, delete-orphan",
    )
