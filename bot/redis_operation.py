import redis
from dotenv import load_dotenv

load_dotenv()

redis_client = redis.StrictRedis(
    host="103.157.218.126",
    port=30001,
    db=0,
)

# redis_client = redis.StrictRedis(
#     host=os.environ.get("REDIS_HOST", "localhost"),
#     port=int(os.environ.get("REDIS_PORT", 6379)),
#     db=int(os.environ.get("REDIS_DB", 0)),
# )

# FLUSHDB
redis_client.flushdb()
