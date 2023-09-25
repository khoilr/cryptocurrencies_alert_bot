import json
import os
import pandas as pd

import redis
from dotenv import load_dotenv

import bitget.spot.market_api as market
from bitget.consts import CONTRACT_WS_URL
from bitget.ws.bitget_ws_client import BitgetWsClient, SubscribeReq

load_dotenv()

# Initialize a Redis connection
REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))
REDIS_DB = int(os.environ.get("REDIS_DB", 0))
REDIS_CLIENT = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)

# Bitget API Keys
API_KEY = os.environ.get("BITGET_API_KEY")
SECRET_KEY = os.environ.get("BITGET_SECRET_KEY")
PASSPHRASE = os.environ.get("BITGET_PASSPHRASE")


def append_to_redis_stream(message):
    message_dict = json.loads(message)

    # Add data messages to Redis and group by instId
    for item in message_dict["data"]:
        print(item)

        inst_id = item.pop("instId")
        redis_key = f"ticker:{inst_id}"

        # Use a Redis list to store data for each instId
        REDIS_CLIENT.xadd(
            name=redis_key,
            fields=item,
            maxlen=1000,
        )


def handel_error(message):
    print("handle_error:" + message)


def get_top_100() -> list:
    """
    Returns a list of the top 100 cryptocurrency symbols by USDT volume.
    """
    market_api = market.MarketApi(
        API_KEY,
        SECRET_KEY,
        PASSPHRASE,
        use_server_time=False,
        first=False,
    )

    top_100_raw = market_api.tickers()
    top_100 = top_100_raw.get("data", [])  # type: ignore

    df_top_100 = pd.DataFrame(top_100)
    df_top_100["usdtVol"] = df_top_100["usdtVol"].astype(float)
    df_top_100 = df_top_100.sort_values(by="usdtVol", ascending=False)

    return df_top_100["symbol"].tolist()[:100]  # pylint: disable=unsubscriptable-object


def main():
    client = (
        BitgetWsClient(CONTRACT_WS_URL, need_login=False)  # Use Public API so no need to login
        .api_key(API_KEY)
        .api_secret_key(SECRET_KEY)
        .passphrase(PASSPHRASE)
        .error_listener(handel_error)
        .build()
    )

    top_100 = get_top_100()
    channels = [SubscribeReq("SP", "ticker", symbol) for symbol in top_100]

    client.subscribe(channels, append_to_redis_stream)


if __name__ == "__main__":
    main()
