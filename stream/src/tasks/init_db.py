import json
from datetime import datetime

from src.database.dao.crypto import Crypto as CryptoDAO
from src.logger import logger
from src.modules.binance_api import get_exchange_info, get_rolling_trade


def join_data(exchange_info_data, rolling_trade_data) -> list[dict]:
    """
    Join exchange information and rolling trade count data for cryptocurrency symbols.

    This function combines exchange information and rolling trade count data for cryptocurrency symbols
    by matching symbols and creating a list of dictionaries containing relevant data.

    Parameters:
        exchange_info_data (list[dict]): A list of dictionaries containing exchange information for cryptocurrency symbols.
        rolling_trade_data (list[dict]): A list of dictionaries containing rolling trade count data for cryptocurrency symbols.

    Returns:
        list[dict]: A list of dictionaries containing joined data with symbol, base asset, quote asset, updated timestamp,
                    and trade count.

    Note:
        - The function matches symbols from both datasets and combines relevant information into a single dictionary.
        - It creates a new list of dictionaries with combined data.
    """

    return [
        {
            "symbol": exchange_info["symbol"],
            "base_asset": exchange_info["baseAsset"],
            "quote_asset": exchange_info["quoteAsset"],
        }
        | {
            "updated_at": datetime.fromtimestamp(rolling_trade["closeTime"] / 1000),
            "count": rolling_trade["count"],
        }
        for exchange_info in exchange_info_data
        for rolling_trade in rolling_trade_data
        if rolling_trade["symbol"] == exchange_info["symbol"]
    ]


def insert_to_db():
    """
    Insert cryptocurrency data into the database.

    This function retrieves exchange information and rolling trade data for cryptocurrencies,
    joins them together, and inserts the top 200 cryptocurrencies into the database.

    If an exception occurs during data retrieval, it logs the error, loads cached data from
    'cryptos.json', and uses the cached data instead.

    Returns:
        None
    """

    try:
        # Get exchange info
        exchange_info_data = get_exchange_info()
        symbols = [i["symbol"] for i in exchange_info_data]
        logger.info(f"Got {len(symbols)} symbols from exchange info")

        # Get rolling trade count
        rolling_trade_data = get_rolling_trade(symbols)
        logger.info(f"Got {len(rolling_trade_data)} symbols from rolling trade count")

        # Join data
        cryptos = join_data(exchange_info_data, rolling_trade_data)
        logger.info(f"Got {len(cryptos)} symbols after joining data")

    except Exception as e:  # pylint: disable=broad-except, invalid-name
        # Log error
        logger.error(e)
        logger.info("Using cached data.")

        # Load cached data
        with open("stream/cryptos.json", "r", encoding="utf-8") as f:  # pylint: disable=invalid-name
            cryptos = json.load(f)

    # Insert the top 200 cryptos into the database
    for crypto in cryptos:
        CryptoDAO.upsert(**crypto)
    logger.info("Inserted data into database")
