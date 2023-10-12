from stream.database import Session
from stream.database.models.dto.crypto import Crypto as CryptoDTO

session = Session()


class Crypto:
    @staticmethod
    def upsert(**kwargs) -> CryptoDTO:
        """
        Insert or update
        """
        # convert timestamp to datetime timestamp
        crypto = CryptoDTO(**kwargs)
        session.merge(crypto)
        session.commit()
        return crypto

    @staticmethod
    def get_top(limit: int, ascending: bool = False) -> list[CryptoDTO]:
        """
        Get top n cryptos sorted by count
        """
        return (
            session.query(CryptoDTO)
            .order_by(CryptoDTO.count.asc() if ascending else CryptoDTO.count.desc())
            .limit(limit)
            .all()
        )
