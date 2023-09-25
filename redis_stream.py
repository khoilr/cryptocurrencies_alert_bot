import os
from pprint import pprint

import redis
from dotenv import load_dotenv

load_dotenv()

redis_client = redis.StrictRedis(
    host=os.environ.get("REDIS_HOST", "localhost"),
    port=int(os.environ.get("REDIS_PORT", 6379)),
    db=int(os.environ.get("REDIS_DB", 0)),
)

while True:
    data = redis_client.xread(
        streams={"ticker:BTCUSDT": "$"},
        block=1000,
    )
    pprint(data)
