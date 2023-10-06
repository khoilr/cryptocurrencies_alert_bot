import asyncio
import gc
import json
import os
import traceback
from typing import Union

import psycopg2
import redis
import websockets
from binance.spot import Spot
from dotenv import load_dotenv
from loguru import logger
from psycopg2.extras import RealDictCursor, RealDictRow
from stream.database.models.dao.crypto import Crypto as CryptoDAO
from stream._redis import main as redis_main
from stream.constants import stable_coins
from stream.database import Session
from stream.database.models.crypto import Crypto

REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))
REDIS_DB = int(os.environ.get("REDIS_DB", 0))

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


def exchange_info() -> list[dict]:
    data = spot_client.exchange_info()["symbols"]

    # Filter symbols that match specified criteria
    crypto_data = [
        symbol
        for symbol in data
        if symbol["baseAsset"].upper() not in stable_coins  # Excludes symbols where the base asset is a stablecoin
        and symbol["quoteAsset"].upper() not in stable_coins  # Excludes symbols where the quote asset is a stablecoin
        and symbol["baseAsset"].upper() != "USDT"  # Ensures that the base asset is not "USDT"
        and (
            symbol.get("permissions") is None or "SPOT" in symbol.get("permissions")
        )  # Allows symbols that either don't have a permissions field or have "SPOT" in their permissions.
        and symbol["status"] == "TRADING"  # Filters symbols where the status field is equal to "TRADING.""
    ]

    return crypto_data


def rolling_trade(symbols) -> list[dict]:
    # Retrieve one-week rolling trade count
    data = [
        trade_count
        for symbol_batch in [
            symbols[i : i + 100] for i in range(0, len(symbols), 100)
        ]  # Split symbols into batches of 100
        for trade_count in spot_client.rolling_window_ticker(
            symbols=symbol_batch,
            windowSize="7d",
        )
    ]

    # Remove entries with count = 0
    data = [symbol for symbol in data if symbol["count"] != 0]

    return data


def join_data(exchange_info_data, rolling_trade_data) -> list[dict]:
    return [
        {
            "symbol": exchange_info["symbol"],
            "base_asset": exchange_info["baseAsset"],
            "quote_asset": exchange_info["quoteAsset"],
        }
        | {
            "updated_at": rollong_trade["closeTime"],
            "count": rollong_trade["count"],
        }
        for exchange_info in exchange_info_data
        for rollong_trade in rolling_trade_data
        if rollong_trade["symbol"] == exchange_info["symbol"]
    ]


def insert_to_db():
    """
    Insert cryptos into the database.
    """
    try:
        # Get exchange info
        exchange_info_data = exchange_info()
        symbols = [i["symbol"] for i in exchange_info_data]

        # Get rolling trade count
        rolling_trade_data = rolling_trade(symbols)

        # Join data
        cryptos = join_data(exchange_info_data, rolling_trade_data)
    except Exception as e:  # pylint: disable=broad-except, invalid-name
        # Log error
        logger.error(e)
        logger.info("Using cached data.")

        # Load cached data
        with open("cryptos.json", "r", encoding="utf-8") as f:  # pylint: disable=invalid-name
            cryptos = json.load(f)

    # Insert the top 200 cryptos into the database
    for crypto in cryptos:
        CryptoDAO.upsert(**crypto)


def main():
    """
    Main function.
    """

    insert_to_db()
    asyncio.run(redis_main())


if __name__ == "__main__":
    main()
