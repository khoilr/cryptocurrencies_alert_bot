import sqlalchemy as sa

from stream.database import Base


class User(Base):
    __tablename__ = "users"

    # id (int) – Unique identifier for this user or bot.
    # is_bot (bool) – True, if this user is a bot.
    # first_name (str) – User’s or bot’s first name.
    # last_name (str, optional) – User’s or bot’s last name.
    # username (str, optional) – User’s or bot’s username.
    # language_code (str, optional) – IETF language tag of the user’s language.
    # is_premium (bool, optional) – True, if this user is a Telegram Premium user.

    id = sa.Column(sa.BigInteger, primary_key=True)
    is_bot = sa.Column(sa.Boolean, nullable=False, default=False)
    first_name = sa.Column(sa.String, nullable=False)
    last_name = sa.Column(sa.String)
    username = sa.Column(sa.String)
    language_code = sa.Column(sa.String)
    is_premium = sa.Column(sa.Boolean, nullable=False, default=False)
