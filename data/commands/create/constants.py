"""Constants for create command"""
from uuid import uuid4

# Create states
CRYPTO, INDICATOR, COMPLETE = [str(uuid4()) for _ in range(3)]

# Indicator states
PARAM, INTERVAL, KLINES, CONDITION, CONDITION_VALUE, CONDITION_VALUE_TWO, CONDITION_VALUE_BY = [
    str(uuid4()) for _ in range(7)
]

# Indicators
PRICE, VOLUME, EMA, SMA, DMA, BBANDS, MACD = [str(uuid4()) for _ in range(7)]

# Indicators pagination
PAGINATION_LIMIT = 5

# Intervals
I_1M, I_3M, I_5M, I_15M, I_30M = [str(uuid4()) for _ in range(5)]
I_1H, I_2H, I_4H, I_6H, I_8H, I_12H = [str(uuid4()) for _ in range(6)]
I_1D, I_3D, I_1W, I_1MONTH = [str(uuid4()) for _ in range(4)]

# Conditions
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
    {"id": INCREASE_TO, "name": "increase_to", "display_name": "Increase To"},
    {"id": DECREASE_TO, "name": "decrease_to", "display_name": "Decrease To"},
    {"id": INCREASE_BY, "name": "increase_by", "display_name": "Increase By"},
    {"id": DECREASE_BY, "name": "decrease_by", "display_name": "Decrease By"},
    {"id": REACH_TO, "name": "reach_to", "display_name": "Reach To"},
    {"id": ENTER_BOUND, "name": "enter_bound", "display_name": "Enter Bound"},
    {"id": EXIT_BOUND, "name": "exit_bound", "display_name": "Exit Bound"},
]

create_welcome_message = """
Get read to create your crypto alert with Cryptocurrencies Alert Bot! 🚀

Pick a coin 🪙, choose indicators 📊, set conditions 🚦, define the value 📈, and add extra options if needed 🌟.\
Stay informed, trade smart 🤑, and level up your crypto adventure! 💪🌟
"""

input_crypto_message = """
To set up your crypto alert, please enter the crypto pair you want to monitor. You can type the pair in yourself. 💬

For example, you can simply type "BTCUSDT" or any other crypto pair. Once you've entered the pair, \
we'll move on to defining the alert indicators and conditions. 📈📉

We support up to the top 500 crypto pairs, so feel free to enter your specific choice. 💰
"""

input_crypto_again_message = """
It appears the crypto pair you entered is not on our supported list of top 500 pairs. 🙁

Please enter a valid crypto pair that we support. Let's find a supported pair and continue setting up your alert! 🚀📈💬
"""

input_indicator_message = """
Great! Please select the indicator you'd like to monitor for your alert from the buttons below. 📊🚀
"""

input_condition_message = """
Now, let's pick a condition for your alert. \
Please choose a condition for your alert by tapping on one of the following options:

🔼 Increase To - Alert when the value increases to a specific threshold.
🔽 Decrease To - Alert when the value decreases to a specific threshold.
📈 Increase By - Alert when the value increases by a certain amount.
📉 Decrease By - Alert when the value decreases by a certain amount.
🎯 Reach To - Alert when the value reaches a particular level.
⏬ Enter Bound - Alert when the value enters a predefined range.
⏫ Exit Bound - Alert when the value exits a predefined range.
"""

input_two_values_message = """
To set a **Bound** condition, please enter two positive numbers separated by a comma (**,**). \
Ensure that the **first number is less than the second**.

For example, you can input: `45.5, 50.0` to define a bound between 45.5 and 50.0.

Please use this format to continue: 📈📉💬
"""

input_value_percentage_message = """
For the **Increase By** or **Decrease By** condition, please enter a **positive number**. \
You can include a percentage sign (%) at the end to indicate a relative change. 💹

For an absolute value, you can enter, for instance, `5` or `10.5`. 📈
If you want to specify a relative change, you can input, for example, `3%` or `7.5%`. 📉

Please provide your value in one of these formats to continue. 💬🚀📊
"""

input_value_message = """
Please enter a **positive number**. 📊🚀

This value should represent your specific criteria. \
Whether it's a threshold, target, or another measure, it must be a positive number to proceed. 💬

Ensure your input is greater than zero to continue. 📈🔢
"""
