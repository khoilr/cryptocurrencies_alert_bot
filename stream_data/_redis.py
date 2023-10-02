import asyncio
import gc
import json
import os
from typing import Union

import psycopg2
import redis
import websockets
from dotenv import load_dotenv
from loguru import logger
from psycopg2.extras import RealDictCursor, RealDictRow

load_dotenv()

logger.add("logs/redis.log", rotation="500 mb")

REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))
REDIS_DB = int(os.environ.get("REDIS_DB", 0))

POSTGRES_HOST = os.environ.get("POSTGRES_HOST", "localhost")
POSTGRES_PORT = int(os.environ.get("POSTGRES_PORT", 5432))
POSTGRES_DB = os.environ.get("POSTGRES_DB", "db")
POSTGRES_USER = os.environ.get("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD", "khoikhoi")


def get_top_cryptos(n_cryptos: Union[None, int] = None) -> list[RealDictRow]:
    postgres_client = psycopg2.connect(
        dbname=POSTGRES_DB,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
    )
    logger.info(f"PostgreSQL client created: {postgres_client}")

    # get top cryptos from database table cryptos sort by count
    with postgres_client.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute("SELECT * FROM cryptos ORDER BY count DESC")
        cryptos = cursor.fetchall()

    # get top n cryptos
    if n_cryptos is not None:
        cryptos = cryptos[:n_cryptos]

    postgres_client.close()

    return cryptos


def message_handler(message_dict, redis_client):
    if "e" not in message_dict:
        return

    if message_dict["e"] != "kline":
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
    is_closed = int(data["x"])
    quote_volume = data["q"]

    fields = {
        "event_time": event_time,
        "start_time": start_time,
        "close_time": close_time,
        "symbol": symbol,
        "interval": interval,
        "open": _open,
        "close": close,
        "high": high,
        "low": low,
        "base_volume": base_volume,
        "is_closed": is_closed,
        "quote_volume": quote_volume,
    }

    stream_key = f"kline:{interval}:{symbol}"

    try:
        redis_client.xadd(
            stream_key,
            fields=fields,  # type: ignore
            maxlen=1000,
        )
    except redis.exceptions.ConnectionError:  # type: ignore
        pass


async def subscribe_to_stream(symbols_batch, redis_client):
    while True:
        try:
            # pylint: disable=no-member
            async with websockets.connect(  # type: ignore
                "wss://stream.binance.com:9443/ws/kline",
                ping_interval=None,
            ) as websocket:
                params = [f"{x['symbol'].lower()}@kline_1s" for x in symbols_batch]
                await websocket.send(json.dumps({"method": "SUBSCRIBE", "params": params, "id": 1}))
                logger.info(f"Subscribed to {len(symbols_batch)} symbols")

                while True:
                    response = await websocket.recv()
                    message_dict = json.loads(response)

                    message_handler(message_dict, redis_client)

        except websockets.ConnectionClosedError as e:  # type: ignore
            logger.error(f"WebSocket connection closed: {e}")
            await asyncio.sleep(1)  # Wait for 60 seconds before reconnecting


async def cleanup():
    while True:
        await asyncio.sleep(3600)
        gc.collect()


async def main():
    """
    Limitation:
        - 1024 streams per connection
        - 300 connections per 5 minutes per IP
    """

    while True:
        try:
            top = get_top_cryptos(500)
            logger.info(f"Got top {len(top)} cryptos from database")

            redis_pool = redis.ConnectionPool(
                host=REDIS_HOST,
                port=REDIS_PORT,
                db=REDIS_DB,
            )
            redis_client = redis.Redis(connection_pool=redis_pool)

            # Replace list of cryptos
            pipe = redis_client.pipeline(transaction=True)
            pipe.delete("cryptos")
            pipe.lpush("cryptos", *[x["symbol"] for x in top])
            pipe.execute()

            # Create a list of tasks to subscribe to the WebSocket streams concurrently
            symbols_batches = [top[i : i + 100] for i in range(0, len(top), 100)]

            tasks = [subscribe_to_stream(symbols_batch, redis_client) for symbols_batch in symbols_batches]
            tasks.append(cleanup())

            await asyncio.gather(*tasks)

        except Exception as e:  # pylint: disable=broad-except
            logger.error(f"An error occurred: {str(e)}")
            await asyncio.sleep(60)  # Wait for 60 seconds before retrying


if __name__ == "__main__":
    asyncio.run(main())
