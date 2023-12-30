import uuid

import sqlalchemy as sa

from src.database import Base


class Crypto(Base):
    # pylint: disable=not-callable, too-few-public-methods
    """
    Represents a cryptocurrency.

    Attributes:
        id (UUID): The unique identifier of the cryptocurrency.
        symbol (str): The symbol of the cryptocurrency.
        base_asset (str): The base asset of the cryptocurrency.
        quote_asset (str): The quote asset of the cryptocurrency.
        count (int): The count of the cryptocurrency.
        created_at (DateTime): The timestamp when the cryptocurrency was created.
        updated_at (DateTime): The timestamp when the cryptocurrency was last updated.
    """
    __tablename__ = "cryptos"

    # Attributes
    id = sa.Column(sa.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    symbol = sa.Column(sa.String(20), nullable=False, unique=True)
    base_asset = sa.Column(sa.String(10), nullable=False)
    quote_asset = sa.Column(sa.String(10), nullable=False)
    count = sa.Column(sa.Integer, nullable=False)
    created_at = sa.Column(sa.DateTime, nullable=False, server_default=sa.func.now())
    updated_at = sa.Column(sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now())
