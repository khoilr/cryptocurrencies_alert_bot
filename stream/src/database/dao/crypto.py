from database import session
from database.models.models.crypto import Crypto as CryptoDTO


class Crypto:
    @staticmethod
    def upsert(**kwargs) -> CryptoDTO:
        """Update or insert"""
        crypto = CryptoDTO(**kwargs)

        # Check if crypto exists
        existing_crypto = session.query(CryptoDTO).filter(CryptoDTO.symbol == crypto.symbol).first()

        if existing_crypto:
            # Update count
            existing_crypto.updated_at = crypto.updated_at
            existing_crypto.count = crypto.count
            session.commit()
            return existing_crypto
        else:
            # Insert
            session.add(crypto)
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

    @staticmethod
    def get_one(**kwargs) -> CryptoDTO:
        return session.query(CryptoDTO).filter_by(**kwargs).first()

    @staticmethod
    def get_multiple_by_symbols(symbols: list[str]) -> list[CryptoDTO]:
        return session.query(CryptoDTO).filter(CryptoDTO.symbol.in_(symbols)).all()
