import json

import aio_pika

from src.database.dao.crypto import Crypto as CryptoDAO
from src.logger import logger


async def get_top(channel: aio_pika.Channel, message: aio_pika.IncomingMessage):
    """
    Get top N cryptocurrencies by trade count.

    This function gets top N cryptocurrencies by trade count from the database.

    Parameters:
        message (aio_pika.IncomingMessage): A message object containing the request.

    Returns:
        None
    """
    logger.info(f"Got message request from {message.correlation_id}")

    # Get the request data
    data = message.body.decode()
    request = json.loads(data)

    # Get the top N cryptocurrencies by trade count
    top_cryptos = CryptoDAO.get_top(request["n"])
    top_cryptos = list(map(CryptoDAO.to_dict, top_cryptos))

    # Publish the result back as a response
    await channel.default_exchange.publish(
        aio_pika.Message(
            body=json.dumps(top_cryptos).encode(),
            correlation_id=message.correlation_id,
            reply_to=message.reply_to,
        ),
        routing_key=message.reply_to,
    )

    # Acknowledge the message
    await message.ack()

    logger.info(f"Published response to {message.correlation_id}")
