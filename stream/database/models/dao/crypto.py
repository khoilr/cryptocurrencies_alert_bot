from stream.database.models.dto.crypto import Crypto as CryptoDTO
from stream.database import Session

session = Session()


class Crypto:
    @staticmethod
    def upsert(**kwargs):
        """
        Insert or update
        """
        crypto = CryptoDTO(**kwargs)
        session.merge(crypto)
        session.commit()
