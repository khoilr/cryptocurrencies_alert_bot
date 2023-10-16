import asyncio
import gc
import json
import os
import traceback
from datetime import datetime

import redis
import websockets
from binance.spot import Spot
from dotenv import load_dotenv
from loguru import logger

from stream.constants import stable_coins
from database.models.dao.crypto import Crypto as CryptoDAO

REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))
REDIS_DB = int(os.environ.get("REDIS_DB", 0))

# Load environment variables
load_dotenv()

# Config logger
logger.add("log.log", rotation="500 mb")

# Create Binance client
spot_client = Spot()
logger.info("Established Binance client")

# Convert stable coins to uppercase
stable_coins = [stable_coin.upper() for stable_coin in stable_coins]


def get_exchange_info() -> list[dict]:
    """
    Retrieve cryptocurrency exchange information.

    This function fetches exchange information from a spot trading client and filters the data
    based on specified criteria to include only actively trading cryptocurrencies.

    Returns:
        list[dict]: A list of cryptocurrency symbols, and their associated data.

    Note:
        The function filters cryptocurrencies based on the following criteria:
        - Excludes symbols where the base asset is a stable coin (specified in 'stable_coins').
        - Excludes symbols where the quote asset is a stable coin (specified in 'stable_coins').
        - Ensures that the base asset is not "USDT."
        - Allows symbols that either don't have a permissions field or have "SPOT" in their permissions.
        - Filters symbols where the status field is equal to "TRADING."
    """

    data = spot_client.exchange_info()["symbols"]

    # Filter symbols that match specified criteria
    crypto_data = [
        symbol
        for symbol in data
        if symbol["baseAsset"].upper() not in stable_coins  # Excludes symbols where the base asset is a stable coin
        and symbol["quoteAsset"].upper() not in stable_coins  # Excludes symbols where the quote asset is a stable coin
        and symbol["baseAsset"].upper() != "USDT"  # Ensures that the base asset is not "USDT"
        and (
            symbol.get("permissions") is None or "SPOT" in symbol.get("permissions")
        )  # Allows symbols that either don't have a permissions field or have "SPOT" in their permissions.
        and symbol["status"] == "TRADING"  # Filters symbols where the status field is equal to "TRADING.""
    ]

    return crypto_data


def get_rolling_trade(symbols) -> list[dict]:
    """
    Retrieve rolling trade count data for a list of cryptocurrency symbols.

    This function retrieves rolling trade count data for the specified cryptocurrency symbols
    over a one-week rolling window using a spot trading client.

    Parameters:
        symbols (list): A list of cryptocurrency symbols for which rolling trade counts are to be retrieved.

    Returns:
        list[dict]: A list of rolling trade count data for the specified symbols.

    Note:
        - The function splits the list of symbols into batches of 100 to manage API requests.
        - It filters out entries with a count of 0 to exclude symbols with no trades during the rolling window.
    """

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


def message_handler(message_dict, redis_client: redis.Redis):
    """
    Handle incoming WebSocket messages for Kline data and store it in Redis.

    This function processes incoming WebSocket messages related to Kline data for cryptocurrency trading.
    It extracts relevant information from the message, including event time, symbol, and Kline data.
    The extracted data is then stored in a Redis stream for the specified interval and symbol.

    Parameters:
        message_dict (dict): The WebSocket message dictionary containing Kline data.
        redis_client (redis.Redis): An instance of the Redis client for data storage.

    Returns:
        None
    """

    if "e" not in message_dict:
        return

    if message_dict["e"] != "kline" or not message_dict["k"]["x"]:
        return

    event_time = message_dict["E"]
    symbol = message_dict["s"]
    data = message_dict["k"]

    start_time = str(data["t"])
    close_time = str(data["T"])
    interval = data["i"]
    _open = data["o"]
    close = data["c"]
    high = data["h"]
    low = data["l"]
    base_volume = data["v"]
    quote_volume = data["q"]

    fields = {
        "event_time": event_time,
        "start_time": start_time,
        "close_time": close_time,
        "open": _open,
        "close": close,
        "high": high,
        "low": low,
        "base_volume": base_volume,
        "quote_volume": quote_volume,
    }

    stream_key = f"kline:{interval}:{symbol}"

    try:
        redis_client.xadd(
            name=stream_key,
            fields=fields,  # type: ignore
            maxlen=1000,
        )
        logger.info(f"Added to stream {stream_key}")

    except redis.exceptions.ConnectionError:  # type: ignore
        pass


async def subscribe_to_kline_stream(batch: dict, redis_client):
    """
    Subscribe to a Kline WebSocket stream and handle incoming messages.

    This asynchronous function establishes a connection to a Kline WebSocket stream for a specific
    batch of cryptocurrency symbols and their interval. It subscribes to the stream, receives
    real-time data, and passes it to a message handler for further processing.

    Parameters:
        batch (dict): A dictionary containing parameters for subscribing to the WebSocket stream.
        redis_client: An instance of the Redis client for data storage.

    Raises:
        websockets.ConnectionClosedError: If the WebSocket connection is closed unexpectedly.

    Returns:
        None
    """

    while True:
        try:
            # pylint: disable=no-member
            async with websockets.connect(  # type: ignore
                "wss://stream.binance.com:9443/ws/kline",
                ping_interval=None,
                open_timeout=600,
            ) as websocket:
                await websocket.send(
                    json.dumps(
                        {
                            "method": "SUBSCRIBE",
                            "params": batch["params"],
                            "id": 1,
                        }
                    )
                )
                logger.info(f"Subscribed to {batch['id']} interval {batch['interval']}")

                while True:
                    response = await websocket.recv()
                    message_dict = json.loads(response)

                    message_handler(message_dict, redis_client)

        # pylint: disable=invalid-name
        except websockets.ConnectionClosedError as e:  # type: ignore
            logger.error(f"WebSocket connection closed: {e}")
            await asyncio.sleep(1)  # Wait for 60 seconds before reconnecting


async def cleanup():
    """
    Perform periodic memory cleanup.

    This asynchronous function is responsible for performing periodic memory cleanup
    at fixed intervals. It uses asyncio `sleep` function to pause execution for
    a specified period and then triggers the Python garbage collector to reclaim
    memory resources.

    The cleanup interval is set to 3600 seconds (1 hour) by default.

    Returns:
        None
    """

    while True:
        await asyncio.sleep(3600)
        gc.collect()
        logger.info("Performed memory cleanup")


async def stream_data():
    """
    Stream cryptocurrency data updates to Redis using WebSocket streams.

    This asynchronous function continuously streams real-time cryptocurrency data to Redis,
    updating the 'cryptos' set and subscribing to Kline WebSocket streams for various
    symbol-interval combinations.

    Limitations:
        - 1024 streams per connection
        - 300 connections per 5 minutes per IP

    Raises:
        Exception: If an error occurs during streaming or processing data.

    Returns:
        None
    """

    while True:
        try:
            top = CryptoDAO.get_top(500)
            logger.info(f"Got top {len(top)} cryptos from database")

            redis_pool = redis.ConnectionPool(
                host=REDIS_HOST,
                port=REDIS_PORT,
                db=REDIS_DB,
            )
            redis_client = redis.Redis(connection_pool=redis_pool)
            logger.info("Established Redis client")

            # Replace set of crypto
            pipe = redis_client.pipeline(transaction=True)
            pipe.delete("cryptos")
            pipe.zadd("cryptos", {x.symbol: x.count for x in top})  # type: ignore
            pipe.execute()
            logger.info("Updated cryptos set")

            # Create a list of tasks to subscribe to the WebSocket streams concurrently
            cryptos_batches = [top[i : i + 100] for i in range(0, len(top), 100)]
            intervals = [
                "1m",
                "3m",
                "5m",
                "15m",
                "30m",
                "1h",
                "2h",
                "4h",
                "6h",
                "8h",
                "12h",
                "1d",
                "3d",
                "1w",
                "1M",
            ]

            # Create params with each symbols batch and interval
            batches = [
                {
                    "params": [f"{crypto.symbol.lower()}@kline_{interval}" for crypto in cryptos_batch],
                    "interval": interval,
                    "id": f"{cryptos_batch[0].symbol}",
                }
                for cryptos_batch in cryptos_batches
                for interval in intervals
            ]

            tasks = [subscribe_to_kline_stream(batch, redis_client) for batch in batches]
            tasks.append(cleanup())

            await asyncio.gather(*tasks)

        except Exception as e:  # pylint: disable=broad-except, invalid-name
            logger.error(f"An error occurred: {str(e)}")
            logger.error(traceback.format_exc())
            await asyncio.sleep(5)  # Wait for 5 seconds before retrying


def main():
    """
    Main function.

    This function serves as the entry point of the program. It calls `insert_to_db()`
    to insert data into the database and runs `stream_data()` asynchronously to stream data.

    Returns:
        None
    """

    logger.info("Starting streaming service")

    insert_to_db()
    asyncio.run(stream_data())


if __name__ == "__main__":
    main()
