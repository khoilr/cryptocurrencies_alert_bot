import os

import redis
from dotenv import load_dotenv

load_dotenv()
# FLUSHDB
redis_client = redis.StrictRedis(
    host=os.environ.get("REDIS_HOST", "localhost"),
    port=int(os.environ.get("REDIS_PORT", 6379)),
    db=int(os.environ.get("REDIS_DB", 0)),
)
redis_client.flushdb()
