# Define conversation states
from pprint import pprint

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Application,
    CallbackContext,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

# Define conversation states
START, CRYPTO, INDICATOR, CONDITION, UNIT, VALUE = range(6)

# Initialize a dictionary to store user data during the conversation
user_data = {}


# Function to start the /create command
async def start_create(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text(
        "Welcome to the Alert Creation Wizard! You will go through a few steps to set up your alert. Let's get started."
    )

    # reply keyboard
    keyboard = [["BTC", "ETH", "BNB"], ["ADA", "SOL", "XRP"]]
    await update.message.reply_text(
        "Please select a cryptocurrency from the list below or type in a crypto symbol you want:",
        reply_markup=ReplyKeyboardMarkup(
            keyboard,
            one_time_keyboard=True,
            input_field_placeholder="What crypto?",
        ),
    )
    return CRYPTO


# Function to ask for a crypto symbol
async def select_crypto(update: Update, context: CallbackContext) -> int:
    keyboard = [
        [
            InlineKeyboardButton("💲 Price", callback_data="price"),
            InlineKeyboardButton("📊 Volume", callback_data="volume"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Please select a cryptocurrency from the list below or type in a crypto symbol you want:",
        reply_markup=reply_markup,
    )
    return INDICATOR


# Function to handle indicator selection
async def select_indicator(update: Update, context: CallbackContext) -> int:
    user_data["indicator"] = update.callback_query.data
    await update.callback_query.message.edit_text(
        f"Great! When do you want to be alerted regarding {user_data['crypto']}'s "
        f"{user_data['indicator']}?\n\n"
        "Choose one of the following options:",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("Increase to", callback_data="increase_to"),
                    InlineKeyboardButton("Decrease to", callback_data="decrease_to"),
                    InlineKeyboardButton("Increase by", callback_data="increase_by"),
                    InlineKeyboardButton("Decrease by", callback_data="decrease_by"),
                ]
            ]
        ),
    )
    return UNIT


# Function to handle condition selection
async def select_condition(update: Update, context: CallbackContext) -> int:
    user_data["condition"] = update.callback_query.data
    await update.callback_query.message.edit_text(
        f"Got it! Do you want to set the value in 'Price' or 'Percentage'?",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("Price", callback_data="price"),
                    InlineKeyboardButton("Percentage", callback_data="percentage"),
                ]
            ]
        ),
    )
    return ConversationHandler.END

    # return VALUE


# Function to cancel the alert creation
async def cancel(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text("Alert creation canceled.")
    return ConversationHandler.END


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query
    option = query.data

    pprint(query)

    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    await query.answer()

    await query.edit_message_text(text=f"Selected option: {query.data}")
    await update.message.reply_text(
        "Please select a cryptocurrency from the list below or type in a crypto symbol you want:"
    )


def command():
    return ConversationHandler(
        entry_points=[CommandHandler("create", start_create)],
        states={
            CRYPTO: [MessageHandler(filters.TEXT & ~filters.COMMAND, select_crypto)],
            INDICATOR: [CallbackQueryHandler(select_indicator, pattern=f"^{INDICATOR}$")],
            CONDITION: [CallbackQueryHandler(select_condition, pattern=f"^{CONDITION}$")],
            # UNIT: [MessageHandler(filters.TEXT & ~filters.COMMAND, select_condition)],
            # VALUE: [MessageHandler(filters.TEXT & ~filters.COMMAND, select_unit)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        allow_reentry=True,
    )
