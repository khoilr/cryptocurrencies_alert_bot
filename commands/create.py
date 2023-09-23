"""
This file handles the creation of cryptocurrency alerts through a Telegram bot.

It provides a conversation flow that allows users to set up cryptocurrency alerts with the following steps:  # pylint: disable=line-too-long
1. Choose the cryptocurrency.
2. Select an indicator (e.g., price, volume, EMA, SMA).
3. Pick one of four conditions: increase to, increase by, decrease to, or decrease by.
4. Input the specific value or percentage for the alert.

The alert configuration is stored in a dictionary named `user_data`.

States:
- CRYPTO: Choosing the cryptocurrency.
- INDICATORS: Selecting the indicator.
- CONDITION: Picking the condition.
- VALUE: Inputting the value or percentage.

Constants:
- PRICE, VOLUME, EMA, SMA: Indicator IDs.
- indicators: A list of indicator options.
- INCREASE_BY, INCREASE_TO, DECREASE_BY, DECREASE_TO: Condition IDs.
- conditions: A list of condition options.

Variables:
- reply_string: A string to store user input.
- user_data: A dictionary to store user input data.

Functions:
- input_crypto: Handles the start of the conversation and receives cryptocurrency input.
- input_indicator: Receives the indicator input.
- input_condition: Receives the condition input.
- input_value: Receives the unit input.
- final_state: Receives the value input and completes the conversation.
- command: Defines the conversation handler for the /create command.

Usage:
The `command` function returns a `ConversationHandler` object that can be added to a Telegram bot's dispatcher to handle the /create command.
"""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.helpers import escape_markdown
from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

# States
CRYPTO, INDICATORS, CONDITION, VALUE = range(4)

# Constants
PRICE, VOLUME, EMA, SMA = range(11, 15)  # Indicator IDs
indicators = [
    {"id": PRICE, "name": "price", "display_name": "💲 Price"},
    {"id": VOLUME, "name": "price", "display_name": "💰 Volume"},
    {"id": EMA, "name": "ema", "display_name": "EMA (Exponential Moving Average)"},
    {"id": SMA, "name": "sma", "display_name": "SMA (Simple Moving Average)"},
]
INCREASE_BY, INCREASE_TO, DECREASE_BY, DECREASE_TO = range(15, 19)  # Condition IDs
conditions = [
    {"id": INCREASE_TO, "name": "increase_to", "display_name": "📈 Increase to"},
    {"id": INCREASE_BY, "name": "increase_by", "display_name": "➕ Increase by"},
    {"id": DECREASE_TO, "name": "decrease_to", "display_name": "📉 Decrease to"},
    {"id": DECREASE_BY, "name": "decrease_by", "display_name": "➖ Decrease by"},
]


# Variables
reply_string = ""  # pylint: disable=invalid-name \


# Start command handler
async def input_crypto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # pylint: disable=line-too-long
    """
    Handles the start of the cryptocurrency alert creation conversation by asking the user to choose a cryptocurrency.

    Args:
        update (telegram.Update): The incoming update object containing user input.
        context (telegram.ext.ContextTypes.DEFAULT_TYPE): The context object to store user data.

    Returns:
        int: The next conversation state, which is CRYPTO.
    """
    # Clear any existing user data to start fresh for this conversation.
    context.user_data.clear()

    # TODO: Replace this list by querying API for the most popular cryptocurrencies.

    # Define a list of cryptocurrency options for the user to choose from.
    keyboards = [
        ["BTC", "ETH", "BNB"],
        ["ADA", "SOL", "XRP"],
    ]

    # Create a reply keyboard markup with the cryptocurrency options
    reply_markup = ReplyKeyboardMarkup(keyboards, one_time_keyboard=True)

    # Send a welcome message and instructions to choose a cryptocurrency
    await update.message.reply_text(
        """
👋 Welcome to the cryptocurrency alert creation process.

We'll guide you through a few simple steps:
1. Choose your cryptocurrency. 💱
2. Select an indicator (e.g., price, volume, EMA, SMA). 🧮
3. Pick one of four conditions: increase to, increase by, decrease to, or decrease by. ↕️
4. Input the specific value or percentage for your alert. 📝

Let's get started! 🚀
        """,
    )

    # Ask the user to choose a cryptocurrency using the reply keyboard markup.
    await update.message.reply_text(
        """
💱 To create an alert for cryptocurrency, \
you'll start by selecting the cryptocurrency you want to monitor. 
You can do this by either choosing from the list of popular cryptocurrencies below or \
by typing in the name or symbol of your specific cryptocurrency.
""",
        reply_markup=reply_markup,
    )

    # Return the next conversation state, which is CRYPTO.
    return CRYPTO


# Handler to receive the cryptocurrency input
async def input_indicator(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles the user's selection of a cryptocurrency and presents indicator options.

    Args:
        update (telegram.Update): The incoming update object containing user input.
        context (telegram.ext.ContextTypes.DEFAULT_TYPE): The context object to store user data.

    Returns:
        int: The next conversation state, which is INDICATORS.
    """
    # Retrieve the selected cryptocurrency from the user's message.
    crypto = update.message.text

    # Store the selected cryptocurrency in the user's data for later reference.
    context.user_data["crypto"] = [crypto]

    # Create a list of indicator options as inline keyboard buttons.
    keyboards = [
        [
            InlineKeyboardButton(
                indicators[0]["display_name"],
                callback_data=str(indicators[0]["id"]),
            ),
            InlineKeyboardButton(
                indicators[1]["display_name"],
                callback_data=str(indicators[1]["id"]),
            ),
        ],
        *[
            [InlineKeyboardButton(indicator["display_name"], callback_data=str(indicator["id"]))]
            for indicator in indicators[2:]
        ],
    ]

    # Create an inline keyboard markup with indicator options.
    reply_markup = InlineKeyboardMarkup(keyboards)

    # Set the global reply string to include the selected cryptocurrency.
    global reply_string
    reply_string = f"💱 Cryptocurrency: {crypto}"

    # Create a reply message with Markdown formatting to prompt the user to select an indicator.
    reply_message = f"""
```
{reply_string}
```""" + escape_markdown(
        """
🧮 Now, let's determine the indicator you want to use for the alert calculation. \
Please select the indicator you'd like to use from the following options:
""",
        version=2,
    )

    # Send the reply message with indicator options as a Markdown message.
    await update.message.reply_markdown_v2(
        text=reply_message,
        reply_markup=reply_markup,
    )

    # Return the next conversation state, which is INDICATORS.
    return INDICATORS


# Handler to receive the indicator input
async def input_condition(update: Update, context=ContextTypes.DEFAULT_TYPE):
    """
    Handles the user's selection of an indicator and presents condition options.

    Args:
        update (telegram.Update): The incoming update object containing user input.
        context (telegram.ext.ContextTypes.DEFAULT_TYPE): The context object to store user data.

    Returns:
        int: The next conversation state, which is CONDITION.
    """
    # Retrieve the user's callback query.
    query = update.callback_query

    # Extract the indicator ID from the callback data.
    indicator_id = int(query.data)

    # Find the selected indicator based on its ID.
    indicator = next(indicator for indicator in indicators if indicator["id"] == indicator_id)

    # Store the selected indicator in the user's data for later reference.
    context.user_data["indicator"] = indicator

    # Create a list of condition options as inline keyboard buttons.
    keyboards = [
        [
            InlineKeyboardButton(condition["display_name"], callback_data=str(condition["id"]))
            for condition in conditions[i : i + 2]
        ]
        for i in range(0, len(conditions), 2)
    ]

    # Create an inline keyboard markup with condition options.
    reply_markup = InlineKeyboardMarkup(keyboards)

    # Update the global reply string to include the selected indicator.
    global reply_string
    reply_string = f"{reply_string}\n🧮 Indicator: {indicator['display_name']}"

    # Create a reply message with Markdown formatting to prompt the user to select a condition.
    # pylint: disable=line-too-long
    reply_message = f"""
```
{reply_string}
```""" + escape_markdown(
        """
↕️ Now, let's decide the condition that triggers your alert. You currently have four options:

- 📈 Increase to: This condition triggers when the chosen indicator reaches a specific value.
- ➕ Increase by: This condition triggers when the chosen indicator increases by a certain amount or percentage.
- 📉 Decrease to: This condition triggers when the chosen indicator falls to a specific value.
- ➖ Decrease by: This condition triggers when the chosen indicator decreases by a certain amount or percentage.

Please select one of the four conditions:
""",
        version=2,
    )

    # Send an answer to the user's callback query and edit the message to display condition options.
    await query.answer()
    await query.edit_message_text(
        text=reply_message,
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN_V2,
    )

    # Return the next conversation state, which is CONDITION.
    return CONDITION


# Handler to receive the unit input
async def input_value(update: Update, context=ContextTypes.DEFAULT_TYPE):
    """
    Handles the user's selection of a condition and prompts them to input the value or percentage.

    Args:
        update (telegram.Update): The incoming update object containing user input.
        context (telegram.ext.ContextTypes.DEFAULT_TYPE): The context object to store user data.

    Returns:
        int: The next conversation state, which is VALUE.
    """
    # Retrieve the user's callback query.
    query = update.callback_query

    # Extract the condition ID from the callback data.
    condition_id = int(query.data)

    # Find the selected condition based on its ID.
    condition = next(condition for condition in conditions if condition["id"] == condition_id)

    # Store the selected condition in the user's data for later reference.
    context.user_data["condition"] = condition

    # Update the global reply string to include the selected condition.
    global reply_string
    reply_string = f"{reply_string}.\n↕️ Condition: {condition['display_name']}"

    # Create a reply message with Markdown formatting to prompt the user to
    # enter the value or percentage.
    reply_message = f"""
```
{reply_string}
```""" + escape_markdown(
        """
📝 Finally, please enter the specific value or percentage for your chosen condition. \
For example, if you selected "Increase to" and "Value," you can input the target value \
(e.g., 100,000 for $100,000). \
If you selected "Increase by" and "Percentage," you can input the percentage increase \
(e.g., 10 for 10%).

Please enter the value or percentage for your alert condition:
""",
        version=2,
    )

    # Send an answer to the user's callback query and edit the message to prompt for value input.
    await query.answer()
    await query.edit_message_text(
        text=reply_message,
        parse_mode=ParseMode.MARKDOWN_V2,
    )

    # Return the next conversation state, which is VALUE.
    return VALUE


# Handler to receive the value input
async def final_state(update: Update, context=ContextTypes.DEFAULT_TYPE):
    # pylint: disable=line-too-long
    """
    Handles the final step of the cryptocurrency alert creation, stores the alert data, and provides a summary to the user.

    Args:
        update (telegram.Update): The incoming update object containing user input.
        context (telegram.ext.ContextTypes.DEFAULT_TYPE): The context object to store user data.

    Returns:
        int: The end state of the conversation, which is ConversationHandler.END.
    """
    # Retrieve the value input by the user.
    value = update.message.text

    # Store the user's input value in the context's user_data.
    context.user_data["value"] = value

    # Retrieve data from user_data for constructing the summary message.
    crypto = context.user_data["crypto"][0]
    indicator_display_name = context.user_data["indicator"]["display_name"]
    condition_display_name = context.user_data["condition"]["display_name"]
    value = context.user_data["value"]

    # Construct a reply message to summarize the alert configuration.
    reply_message = (
        escape_markdown(
            "🎉 Great! You've successfully configured your crypto alert:\n",
            version=2,
        )
        + f"""
```
- 💱 Cryptocurrency: {crypto}
- 🧮 Indicator: {indicator_display_name}
- ↕️ Condition: {condition_display_name}
- 📝 Alert Value: {value}
```
"""
        + escape_markdown(
            f"""You'll be alerted when the {indicator_display_name} of {crypto} \
{condition_display_name} {value}. Happy trading! 📈💰💹
""",
            version=2,
        )
    )

    # Send the summary message to the user.
    await update.message.reply_markdown_v2(reply_message)

    # TODO: Save the alert data to a database.

    # Return the end state of the conversation, which is ConversationHandler.END.
    return ConversationHandler.END


def command():
    """
    Defines the conversation handler for creating cryptocurrency alerts.

    Returns:
        telegram.ext.ConversationHandler: The conversation handler instance.
    """
    # Define the conversation handler with entry points, states, and fallbacks.
    return ConversationHandler(
        entry_points=[CommandHandler("create", input_crypto)],
        states={
            CRYPTO: [MessageHandler(filters.TEXT & ~filters.COMMAND, input_indicator)],
            INDICATORS: [CallbackQueryHandler(input_condition, pattern=r"^(1[1-4])$")],
            CONDITION: [CallbackQueryHandler(input_value, pattern=r"^(1[5-8])$")],
            VALUE: [MessageHandler(filters.TEXT & ~filters.COMMAND, final_state)],
        },
        fallbacks=[],
        allow_reentry=True,
    )
