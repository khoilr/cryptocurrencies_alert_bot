import asyncio
import json

from binance.spot import Spot
from dotenv import load_dotenv
from loguru import logger

from stream._redis import main as redis_main
from stream.constants import stable_coins
from stream.database import Session
from stream.database.models.crypto import Crypto

# Load environment variables
load_dotenv()

# Config logger
logger.add("logs/postgres.log", rotation="500 mb")

# Create database session
sessison = Session()

# Create Binance client
spot_client = Spot()

# Convert stable coins to uppercase
stable_coins = [stable_coin.upper() for stable_coin in stable_coins]


def filter_trading_symbols(exchange_info):
    """
    Filter trading symbols based on permissions and status.

    Args:
        exchange_info (list): List of trading symbols with their information.

    Returns:
        list: Filtered list of trading symbols.
    """
    filtered_symbols = [
        symbol
        for symbol in exchange_info
        if ("permissions" not in symbol or "SPOT" in symbol["permissions"])
        and symbol["status"] == "TRADING"
    ]
    return filtered_symbols


def upsert_crypto(cryptos: list[dict]):
    """
    Insert cryptos into the database.

    Args:
        cryptos (list): List of cryptos to be inserted into the database.

    Returns:
        None
    """
    for crypto in cryptos:
        crypto_instance = Crypto(
            symbol=crypto["symbol"],
            base_asset=crypto["base_asset"],
            quote_asset=crypto["quote_asset"],
            updated_at=crypto["updated_at"],
            count=crypto["count"],
        )

        sessison.merge(crypto_instance)
        sessison.commit()


def insert_to_db():
    """
    Insert cryptos into the database.
    """
    try:
        exchange_info = spot_client.exchange_info()['symbols']

        # Filter symbols that match specified criteria
        crypto_data = [
            symbol
            for symbol in exchange_info
            if symbol["baseAsset"].upper() not in stable_coins  # Excludes symbols where the base asset is a stablecoin
            and symbol["quoteAsset"].upper() not in stable_coins  # Excludes symbols where the quote asset is a stablecoin
            and symbol["baseAsset"].upper() != "USDT"  # Ensures that the base asset is not "USDT"
            and (symbol.get("permissions") is None or "SPOT" in symbol.get("permissions"))  # Allows symbols that either don't have a permissions field or have "SPOT" in their permissions.
            and symbol["status"] == "TRADING"  # Filters symbols where the status field is equal to "TRADING.""
        ]

        # Retrieve symbol names from crypto_data
        symbols = [data["symbol"] for data in crypto_data]

        # Retrieve one-week rolling trade count
        rolling_trade_count = [
            trade_count
            for symbol_batch in [symbols[i : i + 100] for i in range(0, len(symbols), 100)] # Split symbols into batches of 100
            for trade_count in spot_client.rolling_window_ticker(
                symbols=symbol_batch,
                windowSize="7d",
            )
        ]

        # Remove entries with count = 0
        rolling_trade_count = [
            symbol for symbol in rolling_trade_count if symbol["count"] != 0
        ]

        # Combine data from exchange_info and rolling_trade_count
        cryptos = [
            {
                "symbol": data["symbol"],
                "base_asset": data["baseAsset"],
                "quote_asset": data["quoteAsset"],
            }
            | {
                "updated_at": rolling_count["closeTime"],
                "count": rolling_count["count"],
            }
            for data in crypto_data
            for rolling_count in rolling_trade_count
            if rolling_count["symbol"] == data["symbol"]
        ]
    except:  # pylint: disable=bare-except
        logger.error("Failed to retrieve data from Binance API. Using cached data.")
        with open("cryptos.json", "r", encoding="utf-8") as f: # pylint: disable=invalid-name
            cryptos = json.load(f)

    # Insert the top 200 cryptos into the database
    upsert_crypto(cryptos)


def main():
    """
    Main function.
    """

    insert_to_db()
    asyncio.run(redis_main())


if __name__ == "__main__":
    main()
