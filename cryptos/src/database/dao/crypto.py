from src.database import session
from src.database.models.crypto import Crypto as CryptoDTO


class Crypto:
    """
    Represents a cryptocurrency entity.

    Methods:
    - upsert(**kwargs) -> CryptoDTO: Update or insert a cryptocurrency record.
    - get_top(limit: int, ascending: bool = False) -> list[CryptoDTO]: Get top n cryptocurrencies sorted by count.
    - get_one(**kwargs) -> CryptoDTO: Get a single cryptocurrency record based on the provided criteria.
    - get_many_by_symbols(symbols: list[str]) -> list[CryptoDTO]: Get multiple cryptocurrency records based on the provided symbols.
    - to_dict(crypto: CryptoDTO) -> dict: Convert a cryptocurrency record to a dictionary representation.
    """

    @staticmethod
    def upsert(**kwargs) -> CryptoDTO:
        """
        Upserts a crypto record into the database.

        Args:
            **kwargs: Keyword arguments representing the fields of the crypto record.

        Returns:
            The CryptoDTO object representing the upserted crypto record.
        """
        crypto = CryptoDTO(**kwargs)

        # Check if crypto exists
        existing_crypto = session.query(CryptoDTO).filter(CryptoDTO.symbol == crypto.symbol).first()

        if existing_crypto:
            # Update count
            existing_crypto.updated_at = crypto.updated_at
            existing_crypto.count = crypto.count
            session.commit()
            return existing_crypto

        # Insert
        session.add(crypto)
        session.commit()
        return crypto

    @staticmethod
    def get_top(limit: int, ascending: bool = False) -> list[CryptoDTO]:
        """
        Get top n cryptos sorted by count.

        Parameters:
        - limit (int): The maximum number of cryptocurrencies to retrieve.
        - ascending (bool): Whether to sort the cryptocurrencies in ascending order. Default is False (descending order).

        Returns:
        - list[CryptoDTO]: A list of CryptoDTO objects representing the top cryptocurrencies.
        """
        return (
            session.query(CryptoDTO)
            .order_by(CryptoDTO.count.asc() if ascending else CryptoDTO.count.desc())
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_one(**kwargs) -> CryptoDTO:
        """
        Get a single cryptocurrency record based on the provided criteria.

        Parameters:
        - kwargs: Keyword arguments representing the criteria to filter the cryptocurrency record.

        Returns:
        - CryptoDTO: The matching CryptoDTO object, or None if not found.
        """
        return session.query(CryptoDTO).filter_by(**kwargs).first()

    @staticmethod
    def get_many_by_symbols(symbols: list[str]) -> list[CryptoDTO]:
        """
        Get multiple cryptocurrency records based on the provided symbols.

        Parameters:
        - symbols (list[str]): A list of symbols to filter the cryptocurrency records.

        Returns:
        - list[CryptoDTO]: A list of CryptoDTO objects representing the matching cryptocurrencies.
        """
        return session.query(CryptoDTO).filter(CryptoDTO.symbol.in_(symbols)).all()

    @staticmethod
    def to_dict(crypto: CryptoDTO) -> dict:
        """
        Convert a cryptocurrency record to a dictionary representation.

        Parameters:
        - crypto (CryptoDTO): The cryptocurrency record to convert.

        Returns:
        - dict: A dictionary representing the cryptocurrency record.
        """
        return {
            "symbol": crypto.symbol,
            "base_asset": crypto.base_asset,
            "quote_asset": crypto.quote_asset,
            "count": crypto.count,
            "updated_at": crypto.updated_at.isoformat(),
            "created_at": crypto.created_at.isoformat(),
        }
