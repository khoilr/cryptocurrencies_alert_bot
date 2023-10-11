from uuid import uuid4

# States
CRYPTO, INDICATOR, PARAM, INTERVAL, KLINES, CONDITION, SUB_COMPLETE, CONDITION_VALUE, COMPLETE = [
    str(uuid4()) for _ in range(9)
]

# IDs
PRICE, VOLUME, EMA, SMA, DMA, BBANDS, MACD = [str(uuid4()) for _ in range(7)]
PAGINATION_LIMIT = 5
(
    I_1M,
    I_3M,
    I_5M,
    I_15M,
    I_30M,
    I_1H,
    I_2H,
    I_4H,
    I_6H,
    I_8H,
    I_12H,
    I_1D,
    I_3D,
    I_1W,
    I_1MONTH,
) = [str(uuid4()) for _ in range(15)]
INCREASE_TO, DECREASE_TO, INCREASE_BY, DECREASE_BY, REACH_TO, ENTER_BOUND, EXIT_BOUND = [str(uuid4()) for _ in range(7)]

# Callback data
indicators = [
    {"id": PRICE, "name": "price", "display_name": "Price"},
    {"id": VOLUME, "name": "volume", "display_name": "Volume"},
    {"id": EMA, "name": "ema", "display_name": "Exponential Moving Average (EMA)"},
    {"id": SMA, "name": "sma", "display_name": "Simple Moving Average (SMA)"},
    {"id": DMA, "name": "dma", "display_name": "Dual Moving Average (DMA)"},
    {"id": BBANDS, "name": "bbands", "display_name": "Bollinger Bands (BBANDS)"},
    {
        "id": MACD,
        "name": "macd",
        "display_name": "Moving Average Convergence Divergence (MACD)",
    },
]
intervals = [
    {"id": I_1M, "name": "1m", "display_name": "1 minute"},
    {"id": I_3M, "name": "3m", "display_name": "3 minutes"},
    {"id": I_5M, "name": "5m", "display_name": "5 minutes"},
    {"id": I_15M, "name": "15m", "display_name": "15 minutes"},
    {"id": I_30M, "name": "30m", "display_name": "30 minutes"},
    {"id": I_1H, "name": "1h", "display_name": "1 hour"},
    {"id": I_2H, "name": "2h", "display_name": "2 hours"},
    {"id": I_4H, "name": "4h", "display_name": "4 hours"},
    {"id": I_6H, "name": "6h", "display_name": "6 hours"},
    {"id": I_8H, "name": "8h", "display_name": "8 hours"},
    {"id": I_12H, "name": "12h", "display_name": "12 hours"},
    {"id": I_1D, "name": "1d", "display_name": "1 day"},
    {"id": I_3D, "name": "3d", "display_name": "3 days"},
    {"id": I_1W, "name": "1w", "display_name": "1 week"},
    {"id": I_1MONTH, "name": "1M", "display_name": "1 month"},
]
conditions = [
    {"id": INCREASE_TO, "name": "increase_to", "display_name": "Increase to"},
    {"id": DECREASE_TO, "name": "decrease_to", "display_name": "Decrease to"},
    {"id": INCREASE_BY, "name": "increase_by", "display_name": "Increase by"},
    {"id": DECREASE_BY, "name": "decrease_by", "display_name": "Decrease by"},
    {"id": REACH_TO, "name": "reach_to", "display_name": "Reach to"},
    {"id": ENTER_BOUND, "name": "enter_bound", "display_name": "Enter bound"},
    {"id": EXIT_BOUND, "name": "exit_bound", "display_name": "Exit bound"},
]
