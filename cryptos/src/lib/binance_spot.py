from binance.spot import Spot

from src.constants import STABLE_COINS

spot_client = Spot()

# Convert stable coins to uppercase
stable_coins = [stable_coin.upper() for stable_coin in STABLE_COINS]


def get_exchange_info() -> list[dict]:
    """
    Retrieve cryptocurrency exchange information.

    This function fetches exchange information from a spot trading client and filters the data
    based on specified criteria to include only actively trading cryptocurrencies.

    Returns:
        list[dict]: A list of cryptocurrency symbols, and their associated data.

    Note:
        The function filters cryptocurrencies based on the following criteria:
        - Excludes symbols where the base asset is a stable coin (specified in 'stable_coins').
        - Excludes symbols where the quote asset is a stable coin (specified in 'stable_coins').
        - Ensures that the base asset is not "USDT."
        - Allows symbols that either don't have a permissions field or have "SPOT" in their permissions.
        - Filters symbols where the status field is equal to "TRADING."
    """

    data = spot_client.exchange_info()["symbols"]

    # Filter symbols that match specified criteria
    crypto_data = [
        symbol
        for symbol in data
        if symbol["baseAsset"].upper() not in stable_coins  # Excludes symbols where the base asset is a stable coin
        and symbol["quoteAsset"].upper() not in stable_coins  # Excludes symbols where the quote asset is a stable coin
        and symbol["baseAsset"].upper() != "USDT"  # Ensures that the base asset is not "USDT"
        and (
            symbol.get("permissions") is None or "SPOT" in symbol.get("permissions")
        )  # Allows symbols that either don't have a permissions field or have "SPOT" in their permissions.
        and symbol["status"] == "TRADING"  # Filters symbols where the status field is equal to "TRADING.""
    ]

    return crypto_data


def get_rolling_trade(symbols) -> list[dict]:
    """
    Retrieve rolling trade count data for a list of cryptocurrency symbols.

    This function retrieves rolling trade count data for the specified cryptocurrency symbols
    over a one-week rolling window using a spot trading client.

    Parameters:
        symbols (list): A list of cryptocurrency symbols for which rolling trade counts are to be retrieved.

    Returns:
        list[dict]: A list of rolling trade count data for the specified symbols.

    Note:
        - The function splits the list of symbols into batches of 100 to manage API requests.
        - It filters out entries with a count of 0 to exclude symbols with no trades during the rolling window.
    """

    # Retrieve one-week rolling trade count
    data = [
        trade_count
        for symbol_batch in [
            symbols[i : i + 100] for i in range(0, len(symbols), 100)
        ]  # Split symbols into batches of 100
        for trade_count in spot_client.rolling_window_ticker(
            symbols=symbol_batch,
            windowSize="7d",
        )
    ]

    # Remove entries with count = 0
    data = [symbol for symbol in data if symbol["count"] != 0]

    return data
