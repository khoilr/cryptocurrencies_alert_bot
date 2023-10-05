import json

from binance.spot import Spot
from dotenv import load_dotenv
from loguru import logger

from stream.constants import stable_coins
from stream.database import Session
from stream.database.models.crypto import Crypto

load_dotenv()

logger.add("logs/postgres.log", rotation="500 mb")

sessison = Session()

stable_coins = [stable_coin.upper() for stable_coin in stable_coins]
spot_client = Spot()


def get_exchange_info():
    """
    Retrieve exchange information for all trading symbols.

    Returns:
        list: A list of trading symbols with their information.
    """
    exchange_info = spot_client.exchange_info()
    return exchange_info["symbols"]


def filter_trading_symbols(exchange_info):
    """
    Filter trading symbols based on permissions and status.

    Args:
        exchange_info (list): List of trading symbols with their information.

    Returns:
        list: Filtered list of trading symbols.
    """
    filtered_symbols = [
        symbol
        for symbol in exchange_info
        if ("permissions" not in symbol or "SPOT" in symbol["permissions"])
        and symbol["status"] == "TRADING"
    ]
    return filtered_symbols


def save_to_json(data, filename):
    """
    Save data to a JSON file.

    Args:
        data: Data to be saved.
        filename (str): Name of the output JSON file.
    """
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def insert_cryptos(cryptos: list[dict]):
    for crypto in cryptos:
        crypto_instance = Crypto(
            symbol=crypto["symbol"],
            base_asset=crypto["base_asset"],
            quote_asset=crypto["quote_asset"],
            updated_at=crypto["updated_at"],
            count=crypto["count"],
        )

        sessison.merge(crypto_instance)
        sessison.commit()


def main():
    try:
        exchange_info = get_exchange_info()
        filtered_symbols = filter_trading_symbols(exchange_info)
        save_to_json(filtered_symbols, "exchange_info.json")

        # Filter symbols that match specified criteria
        filtered_symbols = [
            symbol
            for symbol in filtered_symbols
            if symbol["baseAsset"].upper() not in stable_coins
            and symbol["quoteAsset"].upper() not in stable_coins
            and symbol["baseAsset"].upper() != "USDT"
        ]

        symbols = [symbol["symbol"] for symbol in filtered_symbols]

        # Retrieve one-week rolling trade count in batches
        rolling_trade_count = [
            trade_count
            for symbol_batch in [
                symbols[i : i + 100] for i in range(0, len(symbols), 100)
            ]
            for trade_count in spot_client.rolling_window_ticker(
                symbols=symbol_batch,
                windowSize="7d",
            )
        ]
        save_to_json(rolling_trade_count, "rolling_window.json")

        # Remove entries with count = 0
        rolling_trade_count = [
            symbol for symbol in rolling_trade_count if symbol["count"] != 0
        ]

        # Combine data from exchange_info and rolling_trade_count
        cryptos = [
            {
                "symbol": symbol["symbol"],
                "base_asset": symbol["baseAsset"],
                "quote_asset": symbol["quoteAsset"],
            }
            | {
                "updated_at": rolling_count["closeTime"],
                "count": rolling_count["count"],
            }
            for symbol in filtered_symbols
            for rolling_count in rolling_trade_count
            if rolling_count["symbol"] == symbol["symbol"]
        ]
        save_to_json(cryptos, "cryptos.json")
    except:  # pylint: disable=bare-except
        with open("cryptos.json", "r", encoding="utf-8") as f:
            cryptos = json.load(f)

    # Sort and get the top 200 cryptos by count descending
    top_cryptos = sorted(cryptos, key=lambda crypto: crypto["count"], reverse=True)

    # Insert the top 200 cryptos into the database
    insert_cryptos(top_cryptos)


if __name__ == "__main__":
    main()
