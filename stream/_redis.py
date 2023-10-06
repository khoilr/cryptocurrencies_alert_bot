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
import traceback

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


async def subscribe_to_stream(batch: dict, redis_client):
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

    logger.info("Starting Redis streaming service")

    while True:
        try:
            top = CryptoDTO.get_top(500)
            logger.info(f"Got top {len(top)} cryptos from database")

            redis_pool = redis.ConnectionPool(
                host=REDIS_HOST,
                port=REDIS_PORT,
                db=REDIS_DB,
            )
            redis_client = redis.Redis(connection_pool=redis_pool)
            logger.info(f"Redis client created: {redis_client}")

            # Replace set of crypto
            pipe = redis_client.pipeline(transaction=True)
            pipe.delete("cryptos")
            pipe.zadd("cryptos", {x["symbol"]: int(x["count"]) for x in top})
            pipe.execute()
            logger.info("Updated cryptos set")

            # Create a list of tasks to subscribe to the WebSocket streams concurrently
            symbols_batches = [top[i : i + 100] for i in range(0, len(top), 100)]
            intervals = ["1m", "3m", "5m", "15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d", "3d", "1w", "1M"]

            # Create params with each symbols batch and interval
            batches = [
                {
                    "params": [f"{symbol['symbol'].lower()}@kline_{interval}" for symbol in symbols_batch],
                    "interval": interval,
                    "id": f"{symbols_batch[0]['symbol']}",
                }
                for symbols_batch in symbols_batches
                for interval in intervals
            ]

            tasks = [subscribe_to_stream(batch, redis_client) for batch in batches]
            tasks.append(cleanup())

            await asyncio.gather(*tasks)

        except Exception as e:  # pylint: disable=broad-except
            logger.error(f"An error occurred: {str(e)}")
            logger.error(traceback.format_exc())
            await asyncio.sleep(5)  # Wait for 60 seconds before retrying


if __name__ == "__main__":
    asyncio.run(main())
