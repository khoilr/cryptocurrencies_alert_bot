import os

from dotenv import load_dotenv

from src.lib.init_data import insert_to_db
from src.services.rabbitmq import RabbitMQService

load_dotenv()
rabbitmq_host = os.environ.get("RABBITMQ_HOST")
rabbitmq_port = int(os.environ.get("RABBITMQ_PORT"))
rabbitmq_user = os.environ.get("RABBITMQ_USER")
rabbitmq_password = os.environ.get("RABBITMQ_PASS")
rabbitmq_vhost = os.environ.get("RABBITMQ_VHOST")


async def app():
    """
    This function represents the main application logic.

    It inserts data to the database and sets up a RabbitMQ service for RPC server.
    """
    insert_to_db()

    rabbitmq_service = RabbitMQService(
        {
            "host": rabbitmq_host,
            "port": rabbitmq_port,
            "login": rabbitmq_user,
            "password": rabbitmq_password,
            "vhost": rabbitmq_vhost,
        }
    )
    await rabbitmq_service.connect()
    await rabbitmq_service.rpc_server()
