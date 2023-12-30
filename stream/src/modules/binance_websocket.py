from src.database.dao.crypto import Crypto as CryptoDAO
from src.logger import logger


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
