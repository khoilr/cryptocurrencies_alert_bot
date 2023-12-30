import asyncio

import aio_pika

from src.logger import logger
from src.services.rabbitmq.handlers.get_top import get_top


class RabbitMQService:
    """
    A class representing a RabbitMQ service.

    Attributes:
        config (dict): The configuration settings for RabbitMQ.
        connection: The RabbitMQ connection object.
        channel: The RabbitMQ channel object.

    Methods:
        connect: Connects to RabbitMQ.
        on_request_get_top: Handles the 'crypto.get_top' request.
        consume_queue: Consumes a specified queue.
        rpc_server: Starts the RPC server.
    """

    def __init__(self, config):
        """
        Initializes a RabbitMQService instance.

        Args:
            config (dict): The configuration settings for RabbitMQ.
        """
        self.config = config
        self.connection = None
        self.channel = None

    async def connect(self):
        """
        Connects to the RabbitMQ server using the provided configuration.

        Returns:
            None

        Raises:
            ConnectionError: If unable to establish a connection to the RabbitMQ server.
        """
        self.connection = await aio_pika.connect_robust(
            host=self.config["host"],
            port=self.config["port"],
            login=self.config["login"],
            password=self.config["password"],
            virtualhost=self.config["vhost"],
        )
        self.channel = await self.connection.channel()
        logger.info("Connected to RabbitMQ")

    async def on_request_get_top(self, message: aio_pika.IncomingMessage):
        """
        Handles the 'crypto.get_top' request.

        Args:
            message (aio_pika.IncomingMessage): The incoming message object.
        """
        await get_top(self.channel, message)

    async def consume_queue(self, queue_name: str, handler: callable):
        """
        Consumes a specified queue.

        Args:
            queue_name (str): The name of the queue to consume.
            handler (callable): The handler function to process each message from the queue.
        """
        queue = await self.channel.declare_queue(queue_name, durable=True)
        logger.info(f"Started consuming queue {queue_name}")
        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                await handler(message)

    async def rpc_server(self):
        """
        Starts the RPC server.
        """
        logger.info("Starting RPC server")
        consume_tasks = [asyncio.create_task(self.consume_queue("crypto.get_top", self.on_request_get_top))]
        await asyncio.gather(*consume_tasks)
