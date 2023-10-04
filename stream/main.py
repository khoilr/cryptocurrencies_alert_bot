import asyncio

from stream._redis import main as redis_main
from stream.postgres import main as postgres_main


def main():
    postgres_main()
    asyncio.run(redis_main())


if __name__ == "__main__":
    main()
