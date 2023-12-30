import asyncio
import gc
import json
import os
import traceback

import redis
import websockets
from binance.spot import Spot
from dotenv import load_dotenv
from loguru import logger

from src.constants import stable_coins
from src.database.dao.crypto import Crypto as CryptoDAO
from src.tasks.init_db import insert_to_db

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


def app():
    """
    Main function.

    This function serves as the entry point of the program. It calls `insert_to_db()`
    to insert data into the database and runs `stream_data()` asynchronously to stream data.

    Returns:
        None
    """

    logger.info("Starting streaming service")

    insert_to_db()


#     asyncio.run(stream_data())


# if __name__ == "__main__":
#     main()
