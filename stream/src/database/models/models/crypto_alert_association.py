import sqlalchemy as sa

from database import Base

# Create the auxiliary table
crypto_alert_association = sa.Table(
    "crypto_alert_association",
    Base.metadata,
    sa.Column("crypto_id", sa.UUID, sa.ForeignKey("cryptos.id")),
    sa.Column("alert_id", sa.UUID, sa.ForeignKey("alerts.id")),
)
